from typing import Dict
from pydantic import BaseModel, Field

class ReviewStats(BaseModel):
    accepted: int = Field(0, description="Total cases accepted by human reviewers")
    edited: int = Field(0, description="Total cases edited by human reviewers")
    rejected: int = Field(0, description="Total cases rejected by human reviewers")
    pending: int = Field(0, description="Total cases awaiting human review")

class DashboardMetricsResponse(BaseModel):
    total_cases: int = Field(..., description="Total number of cases in database")
    total_diagnoses: int = Field(..., description="Total number of diagnoses created")
    reviews: ReviewStats = Field(..., description="Breakdown of human review verdicts")
    agreement_rate: float = Field(..., ge=0.0, le=1.0, description="Rate of agreement between AI diagnosis and deterministic rule engine")
    issue_distribution: Dict[str, int] = Field(default_factory=dict, description="Distribution of issues by category / OSI layer")
    severity_distribution: Dict[str, int] = Field(default_factory=dict, description="Distribution of rule findings by severity level")
    conflicts_count: int = Field(0, description="Total cases with detected conflict between AI and rules")
    insufficient_evidence_count: int = Field(0, description="Total cases flagged as having insufficient evidence")
