import pytest
from fastapi.testclient import TestClient

def test_dashboard_metrics_calculation(client: TestClient, sample_case_payload: dict):
    # Initial state (0 cases)
    res = client.get("/api/dashboard/metrics")
    assert res.status_code == 200
    metrics = res.json()
    assert metrics["total_cases"] == 0
    assert metrics["total_diagnoses"] == 0
    assert metrics["reviews"]["accepted"] == 0

    # Create Case 1 -> will have diagnosis
    case1_res = client.post("/api/cases", json=sample_case_payload)
    case1_id = case1_res.json()["id"]

    # Create Case 2 -> duplicate IP case
    dup_payload = {
        "title": "Duplicate IP Case",
        "symptom": "IP conflict on LAN",
        "topology": {"devices": [{"name": "H1"}, {"name": "H2"}]},
        "addressing": [
            {"device": "H1", "ip_address": "192.168.1.100"},
            {"device": "H2", "ip_address": "192.168.1.100"}
        ],
        "show_outputs": {}
    }
    case2_res = client.post("/api/cases", json=dup_payload)
    case2_id = case2_res.json()["id"]

    # Submit Review for Case 1 (ACCEPTED)
    client.post("/api/reviews", json={
        "case_id": case1_id,
        "status": "ACCEPTED",
        "reviewer_name": "Reviewer 1",
        "reviewer_comment": "Approved"
    })

    # Submit Review for Case 2 (EDITED)
    client.post("/api/reviews", json={
        "case_id": case2_id,
        "status": "EDITED",
        "reviewer_name": "Reviewer 2",
        "reviewer_comment": "Reassigned IP",
        "corrected_diagnosis": {"root_cause": "Duplicate IP", "proposed_fix": "Change H2 IP"}
    })

    # Fetch Metrics and verify calculations from DB
    res = client.get("/api/dashboard/metrics")
    assert res.status_code == 200
    metrics = res.json()

    assert metrics["total_cases"] == 2
    assert metrics["total_diagnoses"] == 2
    assert metrics["reviews"]["accepted"] == 1
    assert metrics["reviews"]["edited"] == 1
    assert metrics["reviews"]["rejected"] == 0
    assert metrics["reviews"]["pending"] == 0
    assert isinstance(metrics["agreement_rate"], float)
    assert len(metrics["issue_distribution"]) > 0
    assert "critical" in metrics["severity_distribution"]
    assert metrics["severity_distribution"]["critical"] >= 1  # Duplicate IP is critical severity
