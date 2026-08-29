from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.schemas.rule_finding import RuleFinding
from app.schemas.ai_diagnosis import DiagnosisResponse
from app.schemas.correlation import EvidenceCorrelation
from app.schemas.evaluation import EvaluationResponse
from app.schemas.review import ReviewResponse

class CaseCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Case title or summary")
    symptom: str = Field(..., min_length=1, description="Reported networking problem symptom")
    topology: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Network topology graph (devices and links)")
    addressing: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="IP addressing and VLAN table")
    show_outputs: Optional[Dict[str, Any]] = Field(default_factory=dict, description="CLI show command outputs per device")

class CaseSummaryResponse(BaseModel):
    id: int
    title: str
    symptom: str
    status: str
    confidence: Optional[float] = None
    osi_layer: Optional[str] = None
    created_at: Optional[str] = None

class CaseDetailResponse(BaseModel):
    id: int
    title: str
    symptom: str
    topology: Dict[str, Any] = Field(default_factory=dict)
    addressing: List[Dict[str, Any]] = Field(default_factory=list)
    show_outputs: Dict[str, Any] = Field(default_factory=dict)
    status: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    diagnosis: Optional[DiagnosisResponse] = None
    rule_findings: Optional[List[RuleFinding]] = None
    correlation: Optional[EvidenceCorrelation] = None
    evaluation: Optional[EvaluationResponse] = None
    review: Optional[ReviewResponse] = None
