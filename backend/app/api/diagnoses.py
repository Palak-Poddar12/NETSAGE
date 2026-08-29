from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.ai_diagnosis import DiagnosisResponse
from app.schemas.case import CaseDetailResponse
from app.services.case_service import case_service


class DiagnoseRequest(BaseModel):
    case_id: int = Field(..., ge=1, description="ID of the case to run/return the diagnosis for")


router = APIRouter(tags=["Diagnoses"])


@router.post("/diagnose", response_model=CaseDetailResponse, status_code=status.HTTP_200_OK)
def run_diagnosis(payload: DiagnoseRequest, db: Session = Depends(get_db)):
    """
    Returns the full diagnostic bundle for an existing case.
    The complete pipeline (rules -> AI -> correlation -> evaluation) is executed
    at case creation time (POST /api/cases); this endpoint retrieves the stored result.
    """
    case_detail = case_service.get_case_by_id(db=db, case_id=payload.case_id)
    if not case_detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case {payload.case_id} not found",
        )
    return case_detail


@router.get("/diagnoses/{diagnosis_id}", response_model=DiagnosisResponse, status_code=status.HTTP_200_OK)
def get_diagnosis(diagnosis_id: int, db: Session = Depends(get_db)):
    """Retrieves a single stored AI diagnosis by its ID."""
    diagnosis = case_service.get_diagnosis_by_id(db=db, diagnosis_id=diagnosis_id)
    if not diagnosis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Diagnosis {diagnosis_id} not found",
        )
    return diagnosis