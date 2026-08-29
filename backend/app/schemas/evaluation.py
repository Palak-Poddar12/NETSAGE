from typing import Optional
from pydantic import BaseModel, Field

class EvaluationOutput(BaseModel):
    root_cause_correctness: float = Field(..., ge=0.0, le=1.0, description="Correctness score of root cause")
    evidence_support_score: float = Field(..., ge=0.0, le=1.0, description="Score indicating how well cited evidence matches supplied data")
    osi_layer_match: bool = Field(..., description="Whether OSI layer aligns with the diagnosed fault")
    next_command_quality: str = Field(..., description="Quality rating: HIGH, MEDIUM, LOW, N/A")
    proposed_fix_safety: str = Field(..., description="Safety check: SAFE, CAUTION, DANGEROUS, N/A")
    confidence_calibration: str = Field(..., description="Calibration: WELL_CALIBRATED, OVERCONFIDENT, UNDERCONFIDENT")
    notes: Optional[str] = Field(None, description="Evaluator assessment notes")

class EvaluationResponse(EvaluationOutput):
    id: int
    case_id: int
    diagnosis_id: int
    created_at: Optional[str] = None
