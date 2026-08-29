from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class CaseCreate(BaseModel):
    case_id: str
    category: str
    symptom: str
    topology: str
    addressing: str
    expected_fault: str
    osi_layer: str
    concept: str
    severity: str

class CaseOut(CaseCreate):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class EvidenceCreate(BaseModel):
    case_id: str
    source: str
    device: str
    command: str
    output: str

class EvidenceOut(EvidenceCreate):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class DiagnosisCreate(BaseModel):
    case_id: str

class DiagnosisOut(BaseModel):
    id: int
    case_id: str
    root_cause: Optional[str] = None
    category: Optional[str] = None
    osi_layer: Optional[str] = None
    confidence: Optional[float] = None
    evidence: Optional[str] = None
    rule_findings: Optional[str] = None
    next_command: Optional[str] = None
    fix_steps: Optional[str] = None
    verification_command: Optional[str] = None
    status: str
    human_review_required: bool
    created_at: datetime
    class Config:
        from_attributes = True

class ReviewCreate(BaseModel):
    diagnosis_id: int
    status: str = Field(..., pattern=r"^(ACCEPTED|EDITED|REJECTED)$")
    corrected_diagnosis: Optional[str] = None
    reviewer_comment: Optional[str] = None

class ReviewOut(ReviewCreate):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    total_cases: int
    total_diagnoses: int
    accepted: int
    edited: int
    rejected: int
    pending: int
    agreement_rate: float
    issue_distribution: dict
    severity_distribution: dict
