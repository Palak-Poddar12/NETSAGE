from typing import List, Optional
from pydantic import BaseModel, Field

class AIDiagnosisOutput(BaseModel):
    root_cause: str = Field(..., description="Identified root cause of the network symptom")
    osi_layer: str = Field(..., description="OSI Layer, e.g. Physical (Layer 1), Data Link (Layer 2), Network (Layer 3), Transport (Layer 4)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    reasoning: str = Field(..., description="Step-by-step diagnostic reasoning based on supplied evidence")
    evidence_used: List[str] = Field(default_factory=list, description="Specific evidence items cited from inputs")
    next_diagnostic_command: Optional[str] = Field(None, description="Recommended next command for verification, if needed")
    proposed_fix: Optional[str] = Field(None, description="Proposed network remediation configuration if justified")
    is_insufficient_evidence: bool = Field(False, description="True if evidence is incomplete to form a definitive conclusion")

class DiagnosisResponse(AIDiagnosisOutput):
    id: int
    created_at: Optional[str] = None
