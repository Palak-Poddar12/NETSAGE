from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.review import ReviewCreate, ReviewResponse
from app.services.review_service import review_service

router = APIRouter(prefix="/reviews", tags=["Human Review"])

@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def submit_review(review_in: ReviewCreate, db: Session = Depends(get_db)):
    """
    Submits a human engineer review verdict (ACCEPTED, EDITED, REJECTED).
    Preserves original AI diagnosis and updates case workflow status.
    """
    return review_service.submit_review(db=db, review_in=review_in)
