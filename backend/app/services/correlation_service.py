import re
from typing import Dict, Any, List, Set
from app.schemas.ai_diagnosis import AIDiagnosisOutput
from app.schemas.rule_finding import RuleFinding
from app.schemas.correlation import EvidenceCorrelation

class CorrelationService:
    def correlate(
        self,
        ai_diagnosis: AIDiagnosisOutput,
        rule_findings: List[RuleFinding],
        topology: Dict[str, Any],
        addressing: List[Dict[str, Any]],
        show_outputs: Dict[str, Any]
    ) -> EvidenceCorrelation:
        """
        Correlates AI diagnosis against deterministic rule findings and supplied raw evidence.
        Detects agreement, conflict, unsupported claims, missing evidence, and hallucinations.
        """
        unsupported_claims: List[str] = []
        missing_evidence: List[str] = []
        possible_hallucinations: List[str] = []

        # 1. Inventory all valid known entities from inputs
        known_devices: Set[str] = set()
        known_ips: Set[str] = set()
        known_interfaces: Set[str] = set()

        for d in topology.get("devices", []):
            if isinstance(d, dict) and "name" in d:
                known_devices.add(d["name"].lower())

        for l in topology.get("links", []):
            if isinstance(l, dict):
                if "source" in l: known_devices.add(l["source"].lower())
                if "target" in l: known_devices.add(l["target"].lower())
                if "source_interface" in l: known_interfaces.add(l["source_interface"].lower())
                if "target_interface" in l: known_interfaces.add(l["target_interface"].lower())

        for item in addressing:
            if "device" in item: known_devices.add(str(item["device"]).lower())
            if "interface" in item: known_interfaces.add(str(item["interface"]).lower())
            if "ip_address" in item:
                ip_clean = str(item["ip_address"]).split("/")[0].strip()
                known_ips.add(ip_clean)
            if "default_gateway" in item and item["default_gateway"]:
                gw_clean = str(item["default_gateway"]).split("/")[0].strip()
                known_ips.add(gw_clean)

        for dev_name in show_outputs.keys():
            known_devices.add(str(dev_name).lower())

        # 2. Check for Hallucinations (Unknown IPs or Devices cited by AI)
        combined_ai_text = f"{ai_diagnosis.root_cause} {ai_diagnosis.reasoning} {' '.join(ai_diagnosis.evidence_used)}"
        
        # Regex for IPv4 in AI response
        found_ips = re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", combined_ai_text)
        for ip in found_ips:
            # Exclude standard masks or loopback/default
            if ip not in ("0.0.0.0", "255.255.255.0", "255.255.255.255", "127.0.0.1", "255.0.0.0"):
                if known_ips and ip not in known_ips:
                    # Check if IP was anywhere in show_outputs text
                    raw_show_text = str(show_outputs)
                    if ip not in raw_show_text:
                        possible_hallucinations.append(f"Referenced IP {ip} is not present in network inventory or show outputs.")

        # 3. Check for Unsupported Claims in evidence_used
        for ev in ai_diagnosis.evidence_used:
            # Check if cited command was actually supplied in show_outputs
            cmd_matches = re.findall(r"(show\s+[\w\s-]+)", ev.lower())
            for cmd in cmd_matches:
                clean_cmd = cmd.strip().replace(" ", "_")
                # Look in show_outputs keys
                found_in_show = False
                for dev, cmds in show_outputs.items():
                    if isinstance(cmds, dict):
                        for c in cmds.keys():
                            if clean_cmd in c.lower() or c.lower() in clean_cmd:
                                found_in_show = True
                                break
                if not found_in_show and len(show_outputs) > 0:
                    unsupported_claims.append(f"AI cited command '{cmd}' which was not provided in case telemetry.")

        # 4. Check for Missing Evidence
        if ai_diagnosis.is_insufficient_evidence:
            missing_evidence.append("Diagnostic data is incomplete to confirm root cause without further telemetry.")
        if not show_outputs:
            missing_evidence.append("No CLI show command outputs provided.")
        if not addressing:
            missing_evidence.append("No IP addressing table provided.")

        # 5. Check Agreement vs Conflict between AI and Rule Engine
        failed_rules = [f for f in rule_findings if not f.passed]
        conflict = False
        agreement = True

        if failed_rules:
            # If rules found concrete failures, does AI acknowledge any of them?
            ai_text_lower = combined_ai_text.lower()
            acknowledged = False
            for f in failed_rules:
                if (f.rule_id.replace("_", " ") in ai_text_lower or 
                    f.rule_name.lower() in ai_text_lower or
                    any(dev.lower() in ai_text_lower for dev in f.affected_devices)):
                    acknowledged = True
                    break
            
            if not acknowledged and not ai_diagnosis.is_insufficient_evidence:
                conflict = True
                agreement = False
        else:
            # If all rules passed, but AI claims a deterministic rule failure (e.g. duplicate IP)
            ai_text_lower = combined_ai_text.lower()
            if "duplicate ip" in ai_text_lower or "gateway mismatch" in ai_text_lower:
                conflict = True
                agreement = False

        if conflict:
            explanation = "Conflict detected: AI diagnosis contradicts deterministic network rule findings."
        elif possible_hallucinations or unsupported_claims:
            explanation = "Warning: AI diagnosis contains citations or entities not grounded in supplied evidence."
        elif agreement and not failed_rules and ai_diagnosis.is_insufficient_evidence:
            explanation = "Agreement: Both deterministic engine and AI indicate all basic checks passed, but further telemetry is needed."
        else:
            explanation = "Agreement: AI diagnosis is consistent with deterministic rule findings and grounded in evidence."

        return EvidenceCorrelation(
            agreement=agreement,
            conflict=conflict,
            unsupported_claims=sorted(list(set(unsupported_claims))),
            missing_evidence=sorted(list(set(missing_evidence))),
            possible_hallucinations=sorted(list(set(possible_hallucinations))),
            explanation=explanation
        )

correlation_service = CorrelationService()
