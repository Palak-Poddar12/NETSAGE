from typing import List
from pydantic import BaseModel, Field

class EvidenceCorrelation(BaseModel):
    agreement: bool = Field(..., description="True if AI diagnosis agrees with deterministic rule findings")
    conflict: bool = Field(..., description="True if AI diagnosis contradicts deterministic findings or facts")
    unsupported_claims: List[str] = Field(default_factory=list, description="Claims made by AI without grounding in show outputs or addressing")
    missing_evidence: List[str] = Field(default_factory=list, description="Evidence absent from input that is needed to confirm the root cause")
    possible_hallucinations: List[str] = Field(default_factory=list, description="Referenced devices, IPs, or interfaces that do not exist in the case data")
    explanation: str = Field(..., description="Detailed explanation of correlation analysis")
