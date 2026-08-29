import pytest
from sqlalchemy.orm import Session
from app.models.case import Case
from app.models.diagnosis import Diagnosis
from app.models.evaluation import Evaluation
from app.models.review import Review

def test_create_case_and_relationships(db_session: Session):
    case = Case(
        title="Test Case",
        symptom="Cannot ping server",
        topology={"devices": [{"name": "R1"}]},
        addressing=[{"device": "R1", "ip_address": "10.0.0.1"}],
        show_outputs={"R1": {"show_version": "Cisco IOS 15.0"}},
        status="DIAGNOSED"
    )
    db_session.add(case)
    db_session.commit()
    db_session.refresh(case)

    assert case.id is not None
    assert case.title == "Test Case"
    assert case.status == "DIAGNOSED"

    # Add diagnosis
    diagnosis = Diagnosis(
        case_id=case.id,
        root_cause="Interface Gig0/1 is down",
        osi_layer="Physical (Layer 1)",
        confidence=0.9,
        reasoning="Interface is down in show outputs",
        evidence_used=["show_ip_interface_brief"],
        rule_findings=[],
        correlation={},
        next_diagnostic_command="show interfaces status",
        proposed_fix="no shutdown",
        is_insufficient_evidence=False
    )
    db_session.add(diagnosis)
    db_session.commit()
    db_session.refresh(diagnosis)

    assert diagnosis.id is not None
    assert case.diagnosis.id == diagnosis.id

    # Add evaluation
    evaluation = Evaluation(
        case_id=case.id,
        diagnosis_id=diagnosis.id,
        root_cause_correctness=1.0,
        evidence_support_score=1.0,
        osi_layer_match=True,
        next_command_quality="HIGH",
        proposed_fix_safety="SAFE",
        confidence_calibration="WELL_CALIBRATED",
        notes="All good"
    )
    db_session.add(evaluation)
    db_session.commit()

    assert len(case.evaluations) == 1
    assert case.evaluations[0].root_cause_correctness == 1.0

    # Add review
    review = Review(
        case_id=case.id,
        status="ACCEPTED",
        reviewer_name="Net Admin",
        reviewer_comment="LGTM"
    )
    db_session.add(review)
    db_session.commit()

    assert len(case.reviews) == 1
    assert case.reviews[0].status == "ACCEPTED"

def test_cascade_delete_case(db_session: Session):
    case = Case(
        title="Cascade Case",
        symptom="Issue",
        topology={},
        addressing=[],
        show_outputs={}
    )
    db_session.add(case)
    db_session.commit()

    diagnosis = Diagnosis(
        case_id=case.id,
        root_cause="Test",
        osi_layer="Layer 1",
        confidence=0.8,
        reasoning="Reason",
        evidence_used=[],
        rule_findings=[],
        correlation={}
    )
    db_session.add(diagnosis)
    db_session.commit()

    # Delete case
    db_session.delete(case)
    db_session.commit()

    # Check diagnosis is deleted
    diag_check = db_session.query(Diagnosis).filter(Diagnosis.case_id == case.id).first()
    assert diag_check is None
