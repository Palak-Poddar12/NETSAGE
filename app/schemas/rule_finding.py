from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

class RuleFinding(BaseModel):
    rule_id: str = Field(..., description="Unique identifier of the rule")
    rule_name: str = Field(..., description="Human readable name of the rule")
    passed: bool = Field(..., description="True if no violation detected, False if issue found")
    severity: str = Field(..., description="Severity level: info, low, medium, high, critical")
    details: str = Field(..., description="Detailed description of the finding")
    affected_devices: List[str] = Field(default_factory=list, description="List of device names affected")
    affected_interfaces: List[str] = Field(default_factory=list, description="List of interface names affected")
    evidence: Optional[Dict[str, Any]] = Field(default=None, description="Structured evidence payload for the finding")
