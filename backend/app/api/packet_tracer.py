from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.packet_tracer import (
    PacketTracerCommandEvidence,
    PacketTracerEvidenceUploadResponse,
    PacketTracerCaseEvidence,
    PacketTracerCaseEvidenceListResponse,
    PacketTracerFileImportRequest,
    PacketTracerVerificationRequest,
    PacketTracerVerificationResponse,
)
from app.schemas.case import CaseDetailResponse
from app.services.packet_tracer_service import packet_tracer_service

router = APIRouter(prefix="/packet-tracer", tags=["Cisco Packet Tracer Integration"])

@router.post("/evidence", response_model=PacketTracerEvidenceUploadResponse, status_code=status.HTTP_201_CREATED)
def upload_command_evidence(
    evidence: PacketTracerCommandEvidence,
    db: Session = Depends(get_db)
):
    """
    Uploads a single Cisco show command output collected from Packet Tracer.
    Preserves raw output without modification or fabrication.
    """
    return packet_tracer_service.add_command_evidence(db=db, evidence=evidence)

@router.get("/evidence/{case_id}", response_model=PacketTracerCaseEvidenceListResponse, status_code=status.HTTP_200_OK)
def get_case_evidence(
    case_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieves all imported Packet Tracer evidence records for the specified case.
    """
    return packet_tracer_service.get_case_evidence(db=db, case_id=case_id)

@router.post("/bundle", response_model=CaseDetailResponse, status_code=status.HTTP_201_CREATED)
def import_case_evidence_bundle(
    bundle: PacketTracerCaseEvidence,
    db: Session = Depends(get_db)
):
    """
    Imports a complete Packet Tracer case evidence bundle (topology, addressing, show outputs)
    and executes the deterministic rule engine and AI diagnostic pipeline.
    """
    return packet_tracer_service.import_case_evidence_bundle(db=db, bundle=bundle)

@router.post("/import-file", status_code=status.HTTP_201_CREATED)
def import_evidence_file(
    request: PacketTracerFileImportRequest,
    db: Session = Depends(get_db)
):
    """
    Imports Packet Tracer evidence from raw CLI show transcripts (.txt), CSV tables, or JSON.
    """
    return packet_tracer_service.import_file(db=db, request=request)

@router.post("/diagnose/{case_id}", response_model=CaseDetailResponse, status_code=status.HTTP_200_OK)
def diagnose_imported_evidence(
    case_id: str,
    db: Session = Depends(get_db)
):
    """
    Runs deterministic rules and AI diagnostic reasoning on all evidence imported for the case.
    Returns INSUFFICIENT_EVIDENCE if required diagnostic commands are absent.
    """
    return packet_tracer_service.diagnose_packet_tracer_case(db=db, case_id=case_id)

@router.post("/verify/{case_id}", response_model=PacketTracerVerificationResponse, status_code=status.HTTP_200_OK)
def verify_resolution(
    case_id: str,
    request: PacketTracerVerificationRequest,
    db: Session = Depends(get_db)
):
    """
    Ingests post-fix verification outputs and validates that the network issue is completely resolved.
    Never assumes a fix without concrete post-fix verification telemetry.
    """
    if request.case_id != case_id:
        request.case_id = case_id
    return packet_tracer_service.verify_packet_tracer_case(db=db, request=request)
