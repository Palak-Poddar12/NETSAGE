from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CaseCreate(BaseModel):
    case_id: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., min_length=1, max_length=100)
    symptom: str = Field(..., min_length=1)
    topology: str = Field(..., min_length=1)
    addressing: str = Field(..., min_length=1)
    expected_fault: str = Field(..., min_length=1)
    osi_layer: str = Field(..., min_length=1, max_length=100)
    concept: str = Field(..., min_length=1, max_length=200)
    severity: str = Field(..., min_length=1, max_length=50)


class CaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    case_id: str
    category: str
    symptom: str
    topology: str
    addressing: str
    expected_fault: str
    osi_layer: str
    concept: str
    severity: str
    created_at: datetime
