import re
import csv
import json
import io
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.case import Case
from app.models.packet_tracer_evidence import PacketTracerEvidence
from app.schemas.packet_tracer import (
    CommandOutputItem,
    PacketTracerCommandEvidence,
    PacketTracerEvidenceUploadResponse,
    PacketTracerCaseEvidence,
    PacketTracerEvidenceItemResponse,
    PacketTracerCaseEvidenceListResponse,
    PacketTracerFileImportRequest,
    PacketTracerVerificationRequest,
    PacketTracerVerificationResponse,
)
from app.schemas.case import CaseCreate, CaseDetailResponse
from app.services.case_service import case_service
from app.rules.engine import rule_engine

def normalize_command_name(cmd: str) -> str:
    """Normalizes command strings to standard key identifiers."""
    c = cmd.strip().lower()
    c = re.sub(r"[^\w\s-]", "", c)
    c = re.sub(r"\s+", "_", c)
    
    # Common Cisco aliases
    alias_map = {
        "sh_ip_int_br": "show_ip_interface_brief",
        "sh_ip_interface_brief": "show_ip_interface_brief",
        "show_ip_int_brief": "show_ip_interface_brief",
        "show_ip_int_br": "show_ip_interface_brief",
        "sh_vlan_br": "show_vlan_brief",
        "sh_vlan_brief": "show_vlan_brief",
        "sh_int_trunk": "show_interfaces_trunk",
        "show_int_trunk": "show_interfaces_trunk",
        "sh_int_status": "show_interfaces_status",
        "show_int_status": "show_interfaces_status",
        "sh_ip_route": "show_ip_route",
        "sh_run": "show_running_config",
        "show_run": "show_running_config",
        "sh_access_lists": "show_access_lists",
        "sh_access-lists": "show_access_lists",
        "sh_ip_access_lists": "show_access_lists",
        "sh_ip_dhcp_binding": "show_ip_dhcp_binding",
        "sh_ip_nat_translations": "show_ip_nat_translations",
        "sh_ip_nat_statistics": "show_ip_nat_statistics",
    }
    return alias_map.get(c, c)

class PacketTracerService:
    def add_command_evidence(
        self,
        db: Session,
        evidence: PacketTracerCommandEvidence
    ) -> PacketTracerEvidenceUploadResponse:
        """
        Ingests a single Cisco show/diagnostic command output from Packet Tracer.
        Preserves raw output without modification or fabrication.
        """
        # Find or create corresponding Case
        case_db = self._find_or_create_case(db, evidence.case_id)

        # Store evidence record in DB
        pt_ev = PacketTracerEvidence(
            case_id=case_db.id,
            pt_case_id=evidence.case_id,
            device=evidence.device.strip(),
            command=evidence.command.strip(),
            output=evidence.output.strip(),
            is_verification=False
        )
        db.add(pt_ev)

        # Update case show_outputs dictionary
        show_outputs = dict(case_db.show_outputs or {})
        dev_dict = dict(show_outputs.get(evidence.device.strip(), {}))
        norm_cmd = normalize_command_name(evidence.command)
        dev_dict[norm_cmd] = evidence.output.strip()
        show_outputs[evidence.device.strip()] = dev_dict
        case_db.show_outputs = show_outputs

        db.commit()
        db.refresh(pt_ev)

        return PacketTracerEvidenceUploadResponse(
            success=True,
            case_id=evidence.case_id,
            device=evidence.device.strip(),
            command=evidence.command.strip(),
            evidence_id=pt_ev.id
        )

    def get_case_evidence(self, db: Session, case_id: str) -> PacketTracerCaseEvidenceListResponse:
        """
        Retrieves all imported Packet Tracer evidence records for a given case.
        """
        query = db.query(PacketTracerEvidence).filter(
            (PacketTracerEvidence.pt_case_id == case_id) |
            (PacketTracerEvidence.case_id == (int(case_id) if case_id.isdigit() else -1))
        ).order_by(PacketTracerEvidence.created_at.asc())

        items = query.all()
        results = [
            PacketTracerEvidenceItemResponse(
                id=item.id,
                case_id=item.case_id,
                pt_case_id=item.pt_case_id,
                device=item.device,
                command=item.command,
                output=item.output,
                is_verification=item.is_verification,
                created_at=item.created_at.isoformat() if item.created_at else None
            )
            for item in items
        ]

        return PacketTracerCaseEvidenceListResponse(
            case_id=case_id,
            total_items=len(results),
            evidence=results
        )

    def import_file(
        self,
        db: Session,
        request: PacketTracerFileImportRequest
    ) -> Dict[str, Any]:
        """
        Imports Packet Tracer evidence from TXT CLI transcripts, CSV, or JSON.
        """
        extracted_commands: List[Tuple[str, str, str]] = []

        if request.file_format == "json":
            try:
                data = json.loads(request.content)
                if isinstance(data, dict):
                    show_outputs = data.get("show_outputs", [])
                    if isinstance(show_outputs, list):
                        for item in show_outputs:
                            if isinstance(item, dict) and "device" in item and "command" in item and "output" in item:
                                extracted_commands.append((item["device"], item["command"], item["output"]))
                    elif isinstance(show_outputs, dict):
                        for dev, cmds in show_outputs.items():
                            if isinstance(cmds, dict):
                                for cmd, out in cmds.items():
                                    extracted_commands.append((dev, cmd, str(out)))
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and "device" in item and "command" in item and "output" in item:
                            extracted_commands.append((item["device"], item["command"], item["output"]))
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid JSON content: {str(e)}")

        elif request.file_format == "csv":
            try:
                f = io.StringIO(request.content.strip())
                reader = csv.DictReader(f)
                for row in reader:
                    dev = row.get("device") or row.get("Device") or row.get("hostname")
                    cmd = row.get("command") or row.get("Command") or row.get("cmd")
                    out = row.get("output") or row.get("Output") or row.get("show_output")
                    if dev and cmd and out:
                        extracted_commands.append((dev, cmd, out))
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid CSV content: {str(e)}")

        elif request.file_format == "txt":
            extracted_commands = self._parse_txt_transcript(request.content)

        if not extracted_commands:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid Cisco command outputs could be parsed from the provided content."
            )

        case_db = self._find_or_create_case(
            db,
            request.case_id,
            title=request.title or f"Packet Tracer Case {request.case_id}",
            symptom=request.symptom or f"Troubleshooting case {request.case_id} imported from Packet Tracer"
        )

        show_outputs = dict(case_db.show_outputs or {})
        imported_count = 0

        for dev, cmd, out in extracted_commands:
            if not out or not out.strip():
                continue
            pt_ev = PacketTracerEvidence(
                case_id=case_db.id,
                pt_case_id=request.case_id,
                device=dev.strip(),
                command=cmd.strip(),
                output=out.strip(),
                is_verification=False
            )
            db.add(pt_ev)

            dev_dict = dict(show_outputs.get(dev.strip(), {}))
            norm_cmd = normalize_command_name(cmd)
            dev_dict[norm_cmd] = out.strip()
            show_outputs[dev.strip()] = dev_dict
            imported_count += 1

        case_db.show_outputs = show_outputs
        db.commit()

        return {
            "success": True,
            "case_id": request.case_id,
            "imported_commands_count": imported_count,
            "devices": sorted(list(show_outputs.keys()))
        }

    def import_case_evidence_bundle(
        self,
        db: Session,
        bundle: PacketTracerCaseEvidence
    ) -> CaseDetailResponse:
        """
        Imports a complete Packet Tracer case bundle and executes diagnostic reasoning.
        """
        show_outputs_dict: Dict[str, Dict[str, str]] = {}
        for item in bundle.show_outputs:
            dev = item.device.strip()
            norm_cmd = normalize_command_name(item.command)
            show_outputs_dict.setdefault(dev, {})[norm_cmd] = item.output.strip()

        case_in = CaseCreate(
            title=bundle.title or f"Packet Tracer Case {bundle.case_id}",
            symptom=bundle.symptom or f"Reported issue in Packet Tracer network ({bundle.case_id})",
            topology=bundle.topology if isinstance(bundle.topology, dict) else {"devices": bundle.devices},
            addressing=bundle.addressing or [],
            show_outputs=show_outputs_dict
        )

        case_detail = case_service.create_case(db=db, case_in=case_in)

        # Update pt_case_id on newly created case
        case_db = db.query(Case).filter(Case.id == case_detail.id).first()
        if case_db:
            case_db.pt_case_id = bundle.case_id
            # Ingest evidence items
            for item in bundle.show_outputs:
                db.add(PacketTracerEvidence(
                    case_id=case_db.id,
                    pt_case_id=bundle.case_id,
                    device=item.device.strip(),
                    command=item.command.strip(),
                    output=item.output.strip(),
                    is_verification=False
                ))
            db.commit()
            db.refresh(case_db)

        return case_service.get_case_by_id(db=db, case_id=case_detail.id)

    def diagnose_packet_tracer_case(self, db: Session, case_id: str) -> CaseDetailResponse:
        """
        Runs/re-runs the diagnostic pipeline on all imported evidence for a Packet Tracer case.
        """
        case_db = self._find_case(db, case_id)
        if not case_db:
            raise HTTPException(status_code=404, detail=f"Case '{case_id}' not found")

        case_in = CaseCreate(
            title=case_db.title,
            symptom=case_db.symptom,
            topology=case_db.topology or {},
            addressing=case_db.addressing or [],
            show_outputs=case_db.show_outputs or {}
        )

        return case_service.create_case(db=db, case_in=case_in)

    def verify_packet_tracer_case(
        self,
        db: Session,
        request: PacketTracerVerificationRequest
    ) -> PacketTracerVerificationResponse:
        """
        Ingests post-fix verification outputs and executes deterministic rule verification.
        Only marks case as VERIFIED if all deterministic checks pass and no faults remain.
        """
        case_db = self._find_case(db, request.case_id)
        if not case_db:
            raise HTTPException(status_code=404, detail=f"Case '{request.case_id}' not found")

        # Save verification evidence records
        for item in request.verification_outputs:
            db.add(PacketTracerEvidence(
                case_id=case_db.id,
                pt_case_id=request.case_id,
                device=item.device.strip(),
                command=item.command.strip(),
                output=item.output.strip(),
                is_verification=True
            ))

        # Merge verification outputs with existing show_outputs
        current_outputs = dict(case_db.show_outputs or {})
        for item in request.verification_outputs:
            dev = item.device.strip()
            norm_cmd = normalize_command_name(item.command)
            dev_dict = dict(current_outputs.get(dev, {}))
            dev_dict[norm_cmd] = item.output.strip()
            current_outputs[dev] = dev_dict

        case_db.show_outputs = current_outputs

        # Re-run rule engine on updated state
        findings = rule_engine.run_all(
            topology=case_db.topology or {},
            addressing=case_db.addressing or [],
            show_outputs=current_outputs
        )

        failed_rules = [f for f in findings if not f.passed]

        # Check if verification outputs indicate remaining packet loss
        verification_text = " ".join(item.output.lower() for item in request.verification_outputs)
        has_ping_failure = (
            " 0/5" in verification_text or
            "(0/5)" in verification_text or
            " 0/4" in verification_text or
            "(0/4)" in verification_text or
            "success rate is 0" in verification_text or
            "100% packet loss" in verification_text or
            "100 percent packet loss" in verification_text or
            "destination host unreachable" in verification_text
        )

        if not failed_rules and not has_ping_failure:
            is_resolved = True
            case_status = "VERIFIED"
            summary = "Network resolution verified: All 10 deterministic network rules passed and verification telemetry confirms normal operation."
            case_db.status = case_status
        else:
            is_resolved = False
            case_status = "UNRESOLVED"
            details = [f.details for f in failed_rules]
            if has_ping_failure:
                details.append("Ping verification failed with 0% success rate")
            summary = f"Verification incomplete: Remaining faults detected: {'; '.join(details)}."

        db.commit()

        return PacketTracerVerificationResponse(
            case_id=request.case_id,
            is_resolved=is_resolved,
            status=case_status,
            summary=summary,
            rule_findings=findings
        )

    def _parse_txt_transcript(self, text: str) -> List[Tuple[str, str, str]]:
        """
        Parses multi-device Cisco CLI show command transcripts.
        Recognizes patterns:
        - `DeviceName# show command`
        - `DeviceName(config)# show command`
        - `-- Device: SW1, Command: show vlan brief --`
        """
        results: List[Tuple[str, str, str]] = []
        lines = text.splitlines()

        current_dev: Optional[str] = None
        current_cmd: Optional[str] = None
        current_output_lines: List[str] = []

        prompt_pattern = re.compile(r"^([A-Za-z0-9_-]+)(?:\([A-Za-z0-9_ -]+\))?[#>]+\s*(show\s+\S.*|ping\s+\S.*|debug\s+\S.*|sh\s+\S.*)", re.IGNORECASE)
        header_pattern = re.compile(r"^(?:--+|\*+)?\s*(?:Device|Host):\s*([A-Za-z0-9_-]+)\s*,\s*(?:Command|Cmd):\s*(show\s+\S.*|sh\s+\S.*)", re.IGNORECASE)

        for line in lines:
            m_prompt = prompt_pattern.match(line.strip())
            m_header = header_pattern.match(line.strip())

            if m_prompt or m_header:
                # Flush previous command block
                if current_dev and current_cmd and current_output_lines:
                    out = "\n".join(current_output_lines).strip()
                    if out:
                        results.append((current_dev, current_cmd, out))
                current_output_lines = []

                if m_prompt:
                    current_dev = m_prompt.group(1).strip()
                    current_cmd = m_prompt.group(2).strip()
                elif m_header:
                    current_dev = m_header.group(1).strip()
                    current_cmd = m_header.group(2).strip()
            else:
                if current_dev and current_cmd:
                    current_output_lines.append(line)

        # Flush final command block
        if current_dev and current_cmd and current_output_lines:
            out = "\n".join(current_output_lines).strip()
            if out:
                results.append((current_dev, current_cmd, out))

        return results

    def _find_or_create_case(
        self,
        db: Session,
        case_id: str,
        title: Optional[str] = None,
        symptom: Optional[str] = None
    ) -> Case:
        """Finds existing case or creates a new one for Packet Tracer ingestion."""
        case_db = self._find_case(db, case_id)
        if case_db:
            return case_db

        case_db = Case(
            pt_case_id=case_id,
            title=title or f"Packet Tracer Case {case_id}",
            symptom=symptom or f"Network troubleshooting case {case_id} imported from Cisco Packet Tracer.",
            topology={},
            addressing=[],
            show_outputs={},
            status="PENDING"
        )
        db.add(case_db)
        db.commit()
        db.refresh(case_db)
        return case_db

    def _find_case(self, db: Session, case_id: str) -> Optional[Case]:
        query = db.query(Case).filter(
            (Case.pt_case_id == case_id) |
            (Case.id == (int(case_id) if case_id.isdigit() else -1))
        )
        return query.first()

packet_tracer_service = PacketTracerService()
