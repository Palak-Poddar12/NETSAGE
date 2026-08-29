from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.case import CaseCreate, CaseSummaryResponse, CaseDetailResponse
from app.services.case_service import case_service

router = APIRouter(prefix="/cases", tags=["Cases"])

@router.post("", response_model=CaseDetailResponse, status_code=status.HTTP_201_CREATED)
def create_case(case_in: CaseCreate, db: Session = Depends(get_db)):
    """
    Submits a new network diagnostic case.
    Executes rule engine, AI reasoning, correlation, evaluation, and saves the complete diagnostic bundle.
    """
    return case_service.create_case(db=db, case_in=case_in)

@router.get("", response_model=List[CaseSummaryResponse], status_code=status.HTTP_200_OK)
def list_cases(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by case status"),
    limit: int = Query(50, ge=1, le=100, description="Max records to return"),
    offset: int = Query(0, ge=0, description="Offset pagination"),
    db: Session = Depends(get_db)
):
    """
    Lists summary of submitted cases.
    """
    return case_service.list_cases(db=db, status=status_filter, limit=limit, offset=offset)

@router.get("/{case_id}", response_model=CaseDetailResponse, status_code=status.HTTP_200_OK)
def get_case(case_id: int, db: Session = Depends(get_db)):
    """
    Retrieves full case details including diagnosis, rule findings, correlation, evaluation, and review.
    """
    case_detail = case_service.get_case_by_id(db=db, case_id=case_id)
    if not case_detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Case {case_id} not found")
    return case_detail
