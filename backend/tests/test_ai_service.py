import pytest
from unittest.mock import MagicMock, patch
from app.services.ai_service import AIService
from app.schemas.rule_finding import RuleFinding
from app.schemas.ai_diagnosis import AIDiagnosisOutput

def test_ai_service_fallback_empty_evidence():
    service = AIService(api_key="")
    output = service.diagnose(
        symptom="No link",
        topology={},
        addressing=[],
        show_outputs={},
        rule_findings=[]
    )
    assert isinstance(output, AIDiagnosisOutput)
    assert output.is_insufficient_evidence is True
    assert output.confidence <= 0.2

def test_ai_service_fallback_with_failed_rule():
    service = AIService(api_key="")
    failed_finding = RuleFinding(
        rule_id="interface_down",
        rule_name="Interface Operational State Check",
        passed=False,
        severity="critical",
        details="Gig0/1 is administratively down",
        affected_devices=["R1"],
        affected_interfaces=["R1:Gig0/1"]
    )
    output = service.diagnose(
        symptom="Cannot reach R1",
        topology={"devices": [{"name": "R1"}]},
        addressing=[{"device": "R1", "interface": "Gig0/1", "ip_address": "192.168.1.1"}],
        show_outputs={"R1": {"show_ip_interface_brief": "Gig0/1 192.168.1.1 YES manual administratively down down"}},
        rule_findings=[failed_finding]
    )
    assert isinstance(output, AIDiagnosisOutput)
    assert not output.is_insufficient_evidence
    assert output.confidence >= 0.8
    assert "administratively down" in output.root_cause
    assert output.osi_layer == "Physical (Layer 1)"
    assert output.proposed_fix is not None

def test_ai_service_mock_openai_success():
    mock_client = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = """{
        "root_cause": "Trunk encapsulation misconfiguration",
        "osi_layer": "Data Link (Layer 2)",
        "confidence": 0.95,
        "reasoning": "Trunk port Gig0/24 drops VLAN 10 tags.",
        "evidence_used": ["SW1 show_interfaces_trunk"],
        "next_diagnostic_command": "show interfaces trunk",
        "proposed_fix": "switchport trunk allowed vlan add 10",
        "is_insufficient_evidence": false
    }"""
    mock_client.chat.completions.create.return_value.choices = [mock_choice]

    service = AIService(api_key="sk-mock-key")
    service.client = mock_client

    output = service.diagnose(
        symptom="VLAN 10 isolated",
        topology={},
        addressing=[],
        show_outputs={},
        rule_findings=[]
    )
    assert isinstance(output, AIDiagnosisOutput)
    assert output.root_cause == "Trunk encapsulation misconfiguration"
    assert output.confidence == 0.95
    assert not output.is_insufficient_evidence

def test_ai_service_handles_api_exception_gracefully():
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = Exception("API Timeout")

    service = AIService(api_key="sk-mock-key")
    service.client = mock_client

    output = service.diagnose(
        symptom="Timeout test",
        topology={},
        addressing=[],
        show_outputs={},
        rule_findings=[]
    )
    assert isinstance(output, AIDiagnosisOutput)
    assert output.is_insufficient_evidence is True
