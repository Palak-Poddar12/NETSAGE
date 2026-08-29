import pytest
from app.services.correlation_service import CorrelationService
from app.schemas.ai_diagnosis import AIDiagnosisOutput
from app.schemas.rule_finding import RuleFinding

def test_correlation_agreement():
    service = CorrelationService()
    ai_diag = AIDiagnosisOutput(
        root_cause="Duplicate IP address conflict on 192.168.1.50",
        osi_layer="Network (Layer 3)",
        confidence=0.95,
        reasoning="Both Host A and Host B are configured with 192.168.1.50.",
        evidence_used=["addressing table"],
        next_diagnostic_command="show arp",
        proposed_fix="Change Host B IP to 192.168.1.51",
        is_insufficient_evidence=False
    )
    rule_findings = [
        RuleFinding(
            rule_id="duplicate_ip",
            rule_name="Duplicate IP Address Check",
            passed=False,
            severity="critical",
            details="Duplicate IP 192.168.1.50 detected",
            affected_devices=["Host-A", "Host-B"]
        )
    ]
    topology = {"devices": [{"name": "Host-A"}, {"name": "Host-B"}]}
    addressing = [{"device": "Host-A", "ip_address": "192.168.1.50"}, {"device": "Host-B", "ip_address": "192.168.1.50"}]
    
    res = service.correlate(ai_diag, rule_findings, topology, addressing, {})
    assert res.agreement is True
    assert res.conflict is False
    assert len(res.possible_hallucinations) == 0

def test_correlation_detects_conflict():
    service = CorrelationService()
    ai_diag = AIDiagnosisOutput(
        root_cause="Everything is operating normally with no issues",
        osi_layer="Application (Layer 7)",
        confidence=0.9,
        reasoning="All services healthy",
        evidence_used=[],
        is_insufficient_evidence=False
    )
    rule_findings = [
        RuleFinding(
            rule_id="interface_down",
            rule_name="Interface Operational State Check",
            passed=False,
            severity="critical",
            details="Gig0/1 administratively down",
            affected_devices=["R1"]
        )
    ]
    res = service.correlate(ai_diag, rule_findings, {}, [], {})
    assert res.conflict is True
    assert res.agreement is False

def test_correlation_detects_hallucinations():
    service = CorrelationService()
    ai_diag = AIDiagnosisOutput(
        root_cause="Router R99 interface 10.99.99.1 failed",
        osi_layer="Network (Layer 3)",
        confidence=0.8,
        reasoning="Check 10.99.99.1 on R99",
        evidence_used=[],
        is_insufficient_evidence=False
    )
    topology = {"devices": [{"name": "R1"}]}
    addressing = [{"device": "R1", "ip_address": "192.168.1.1"}]
    
    res = service.correlate(ai_diag, [], topology, addressing, {})
    assert len(res.possible_hallucinations) > 0
    assert any("10.99.99.1" in h for h in res.possible_hallucinations)
