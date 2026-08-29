from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Case
from app.schemas import CaseCreate, CaseResponse

router = APIRouter(prefix="/api")


@router.post(
    "/cases",
    response_model=CaseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_case(
    case_data: CaseCreate,
    db: Session = Depends(get_db),
):
    existing_case = db.scalar(
        select(Case).where(Case.case_id == case_data.case_id)
    )

    if existing_case is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "DUPLICATE_CASE_ID",
                "message": f"Case '{case_data.case_id}' already exists.",
            },
        )

    case = Case(**case_data.model_dump())

    db.add(case)

    try:
        db.commit()
        db.refresh(case)
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "DUPLICATE_CASE_ID",
                "message": f"Case '{case_data.case_id}' already exists.",
            },
        )

    return case


@router.get(
    "/cases",
    response_model=list[CaseResponse],
)
def get_cases(
    db: Session = Depends(get_db),
):
    statement = select(Case).order_by(Case.created_at.desc())

    return list(db.scalars(statement).all())


@router.get(
    "/cases/{case_id}",
    response_model=CaseResponse,
)
def get_case(
    case_id: str,
    db: Session = Depends(get_db),
):
    case = db.scalar(
        select(Case).where(Case.case_id == case_id)
    )

    if case is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "CASE_NOT_FOUND",
                "message": f"Case '{case_id}' does not exist.",
            },
        )

    return case
