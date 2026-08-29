from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.case import Case
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewResponse

class ReviewService:
    def submit_review(self, db: Session, review_in: ReviewCreate) -> ReviewResponse:
        """
        Submits human review verdict: ACCEPTED, EDITED, or REJECTED.
        Preserves original AI diagnosis without modification or deletion.
        Updates Case status to reflect verdict.
        """
        case_db = db.query(Case).filter(Case.id == review_in.case_id).first()
        if not case_db:
            raise HTTPException(status_code=404, detail=f"Case {review_in.case_id} not found")

        # Create review record
        review_db = Review(
            case_id=review_in.case_id,
            status=review_in.status,
            reviewer_name=review_in.reviewer_name,
            reviewer_comment=review_in.reviewer_comment,
            corrected_diagnosis=review_in.corrected_diagnosis
        )
        db.add(review_db)

        # Update case status (without mutating or deleting diagnosis)
        case_db.status = review_in.status

        db.commit()
        db.refresh(review_db)

        return ReviewResponse(
            id=review_db.id,
            case_id=review_db.case_id,
            status=review_db.status,
            reviewer_name=review_db.reviewer_name,
            reviewer_comment=review_db.reviewer_comment,
            corrected_diagnosis=review_db.corrected_diagnosis,
            created_at=review_db.created_at.isoformat() if review_db.created_at else None
        )

review_service = ReviewService()
