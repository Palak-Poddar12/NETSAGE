from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
from app.schemas.rule_finding import RuleFinding
from app.schemas.case import CaseDetailResponse

class CommandOutputItem(BaseModel):
    device: str = Field(..., min_length=1, description="Cisco device hostname e.g. SW1, R1")
    command: str = Field(..., min_length=1, description="Executed Cisco show/diagnostic command e.g. 'show vlan brief'")
    output: str = Field(..., description="Raw output text captured from device CLI")

    @field_validator("output")
    @classmethod
    def validate_non_empty_output(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Command output cannot be empty or whitespace only.")
        return v

class PacketTracerCommandEvidence(BaseModel):
    case_id: str = Field(..., min_length=1, description="Troubleshooting case identifier e.g. 'NET-001'")
    device: str = Field(..., min_length=1, description="Target Cisco device hostname")
    command: str = Field(..., min_length=1, description="Cisco command executed")
    output: str = Field(..., description="Captured CLI output")

    @field_validator("output")
    @classmethod
    def validate_output(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Command output cannot be empty or whitespace only.")
        return v

class PacketTracerEvidenceUploadResponse(BaseModel):
    success: bool = True
    case_id: str
    device: str
    command: str
    evidence_id: Optional[int] = None

class PacketTracerCaseEvidence(BaseModel):
    case_id: str = Field(..., min_length=1, description="Unique case identifier")
    source: str = Field(default="Cisco Packet Tracer", description="Evidence data source")
    title: Optional[str] = Field(default=None, description="Case title")
    symptom: Optional[str] = Field(default=None, description="Reported network symptom")
    topology: Optional[Any] = Field(default=None, description="Topology graph structure or description")
    devices: List[Dict[str, Any]] = Field(default_factory=list, description="List of devices in topology")
    addressing: List[Dict[str, Any]] = Field(default_factory=list, description="IP and VLAN addressing table")
    show_outputs: List[CommandOutputItem] = Field(default_factory=list, description="Structured show command outputs")
    configuration: List[Dict[str, Any]] = Field(default_factory=list, description="Device configuration snippets")
    notes: Optional[str] = Field(default="", description="Operator notes or troubleshooting context")

class PacketTracerEvidenceItemResponse(BaseModel):
    id: int
    case_id: Optional[int] = None
    pt_case_id: str
    device: str
    command: str
    output: str
    is_verification: bool
    created_at: Optional[str] = None

class PacketTracerCaseEvidenceListResponse(BaseModel):
    case_id: str
    total_items: int
    evidence: List[PacketTracerEvidenceItemResponse]

class PacketTracerFileImportRequest(BaseModel):
    case_id: str = Field(..., min_length=1, description="Case identifier e.g. 'NET-001'")
    file_format: str = Field(..., description="File format: 'txt', 'csv', or 'json'")
    content: str = Field(..., min_length=1, description="Raw file contents")
    title: Optional[str] = Field(None, description="Optional case title")
    symptom: Optional[str] = Field(None, description="Optional symptom description")

    @field_validator("file_format")
    @classmethod
    def validate_format(cls, v: str) -> str:
        fmt = v.lower().strip()
        if fmt not in ("txt", "csv", "json"):
            raise ValueError("Supported file formats are: 'txt', 'csv', 'json'")
        return fmt

class PacketTracerVerificationRequest(BaseModel):
    case_id: str = Field(..., min_length=1, description="Case identifier being verified")
    verification_outputs: List[CommandOutputItem] = Field(..., min_length=1, description="Post-fix show/verification command outputs")
    notes: Optional[str] = Field(None, description="Human reviewer verification notes")

class PacketTracerVerificationResponse(BaseModel):
    case_id: str
    is_resolved: bool
    status: str
    summary: str
    rule_findings: List[RuleFinding]
