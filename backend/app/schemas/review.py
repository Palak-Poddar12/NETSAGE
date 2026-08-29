from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, model_validator

class ReviewCreate(BaseModel):
    case_id: int = Field(..., description="ID of the case being reviewed")
    status: str = Field(..., description="Verdict: ACCEPTED, EDITED, or REJECTED")
    reviewer_name: str = Field(..., min_length=1, description="Name or identifier of the reviewer")
    reviewer_comment: str = Field(..., description="Reviewer feedback comment")
    corrected_diagnosis: Optional[Dict[str, Any]] = Field(None, description="Corrected diagnosis payload required for EDITED status")

    @model_validator(mode="after")
    def validate_review_constraints(self):
        status_upper = self.status.upper()
        if status_upper not in ("ACCEPTED", "EDITED", "REJECTED"):
            raise ValueError("Status must be one of: ACCEPTED, EDITED, REJECTED")
        self.status = status_upper

        if not self.reviewer_comment or not self.reviewer_comment.strip():
            raise ValueError("Reviewer comment is required")

        if self.status == "EDITED":
            if not self.corrected_diagnosis:
                raise ValueError("EDITED status requires 'corrected_diagnosis' payload")
            if not isinstance(self.corrected_diagnosis, dict) or len(self.corrected_diagnosis) == 0:
                raise ValueError("EDITED status requires a non-empty 'corrected_diagnosis' dictionary")

        return self

class ReviewResponse(BaseModel):
    id: int
    case_id: int
    status: str
    reviewer_name: str
    reviewer_comment: str
    corrected_diagnosis: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None
