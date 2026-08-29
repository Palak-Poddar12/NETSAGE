import pytest
from app.services.evaluation_service import EvaluationService
from app.schemas.ai_diagnosis import AIDiagnosisOutput
from app.schemas.rule_finding import RuleFinding
from app.schemas.correlation import EvidenceCorrelation

def test_evaluation_high_score_for_aligned_diagnosis():
    service = EvaluationService()
    ai_diag = AIDiagnosisOutput(
        root_cause="VLAN 10 missing on SW1",
        osi_layer="Data Link (Layer 2)",
        confidence=0.9,
        reasoning="SW1 does not have VLAN 10 active.",
        evidence_used=["SW1 show_vlan_brief"],
        next_diagnostic_command="show vlan brief",
        proposed_fix="vlan 10\nname Users",
        is_insufficient_evidence=False
    )
    correlation = EvidenceCorrelation(
        agreement=True,
        conflict=False,
        unsupported_claims=[],
        missing_evidence=[],
        possible_hallucinations=[],
        explanation="Aligned."
    )
    eval_out = service.evaluate(ai_diag, [], correlation)
    assert eval_out.root_cause_correctness == 1.0
    assert eval_out.evidence_support_score == 1.0
    assert eval_out.osi_layer_match is True
    assert eval_out.next_command_quality == "HIGH"
    assert eval_out.proposed_fix_safety == "SAFE"
    assert eval_out.confidence_calibration == "WELL_CALIBRATED"

def test_evaluation_flags_dangerous_fix():
    service = EvaluationService()
    ai_diag = AIDiagnosisOutput(
        root_cause="Bug in memory",
        osi_layer="Network (Layer 3)",
        confidence=0.9,
        reasoning="Reload device",
        evidence_used=[],
        next_diagnostic_command="show version",
        proposed_fix="erase startup-config and reload",
        is_insufficient_evidence=False
    )
    correlation = EvidenceCorrelation(
        agreement=True,
        conflict=False,
        unsupported_claims=[],
        missing_evidence=[],
        possible_hallucinations=[],
        explanation="Aligned."
    )
    eval_out = service.evaluate(ai_diag, [], correlation)
    assert eval_out.proposed_fix_safety == "DANGEROUS"

def test_evaluation_flags_overconfidence_on_conflict():
    service = EvaluationService()
    ai_diag = AIDiagnosisOutput(
        root_cause="Issue solved",
        osi_layer="Network (Layer 3)",
        confidence=0.95,
        reasoning="No issue",
        evidence_used=[],
        is_insufficient_evidence=False
    )
    correlation = EvidenceCorrelation(
        agreement=False,
        conflict=True,
        unsupported_claims=["Cited unsupplied command"],
        missing_evidence=[],
        possible_hallucinations=[],
        explanation="Conflict."
    )
    eval_out = service.evaluate(ai_diag, [], correlation)
    assert eval_out.root_cause_correctness <= 0.3
    assert eval_out.confidence_calibration == "OVERCONFIDENT"
