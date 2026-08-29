import pytest
from fastapi.testclient import TestClient

def test_review_accepted_endpoint(client: TestClient, sample_case_payload: dict):
    case_res = client.post("/api/cases", json=sample_case_payload)
    case_id = case_res.json()["id"]

    review_payload = {
        "case_id": case_id,
        "status": "ACCEPTED",
        "reviewer_name": "Senior Network Engineer",
        "reviewer_comment": "Verified root cause and fix."
    }
    response = client.post("/api/reviews", json=review_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "ACCEPTED"
    assert data["reviewer_name"] == "Senior Network Engineer"

    # Verify case status updated
    case_detail = client.get(f"/api/cases/{case_id}").json()
    assert case_detail["status"] == "ACCEPTED"
    assert case_detail["review"]["status"] == "ACCEPTED"
    # Ensure diagnosis was not modified/deleted
    assert case_detail["diagnosis"] is not None

def test_review_edited_endpoint(client: TestClient, sample_case_payload: dict):
    case_res = client.post("/api/cases", json=sample_case_payload)
    case_id = case_res.json()["id"]

    review_payload = {
        "case_id": case_id,
        "status": "EDITED",
        "reviewer_name": "Lead Architect",
        "reviewer_comment": "Updated root cause to reflect secondary subnet constraint.",
        "corrected_diagnosis": {
            "root_cause": "Trunk VLAN 10 was pruned and IP helper-address missing on subinterface.",
            "osi_layer": "Network (Layer 3)",
            "proposed_fix": "ip helper-address 192.168.100.1"
        }
    }
    response = client.post("/api/reviews", json=review_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "EDITED"
    assert data["corrected_diagnosis"]["root_cause"] == "Trunk VLAN 10 was pruned and IP helper-address missing on subinterface."

    # Verify case status updated to EDITED
    case_detail = client.get(f"/api/cases/{case_id}").json()
    assert case_detail["status"] == "EDITED"
    assert case_detail["review"]["corrected_diagnosis"] is not None

def test_review_edited_missing_corrected_diagnosis_fails_422(client: TestClient, sample_case_payload: dict):
    case_res = client.post("/api/cases", json=sample_case_payload)
    case_id = case_res.json()["id"]

    review_payload = {
        "case_id": case_id,
        "status": "EDITED",
        "reviewer_name": "Engineer",
        "reviewer_comment": "Edited but forgot payload",
        "corrected_diagnosis": None
    }
    response = client.post("/api/reviews", json=review_payload)
    assert response.status_code == 422

def test_review_rejected_endpoint(client: TestClient, sample_case_payload: dict):
    case_res = client.post("/api/cases", json=sample_case_payload)
    case_id = case_res.json()["id"]

    review_payload = {
        "case_id": case_id,
        "status": "REJECTED",
        "reviewer_name": "Escalation Engineer",
        "reviewer_comment": "Issue is a fiber optic break, not an IP issue."
    }
    response = client.post("/api/reviews", json=review_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "REJECTED"

    # Verify case status updated to REJECTED
    case_detail = client.get(f"/api/cases/{case_id}").json()
    assert case_detail["status"] == "REJECTED"

def test_review_rejected_missing_comment_fails_422(client: TestClient, sample_case_payload: dict):
    case_res = client.post("/api/cases", json=sample_case_payload)
    case_id = case_res.json()["id"]

    review_payload = {
        "case_id": case_id,
        "status": "REJECTED",
        "reviewer_name": "Engineer",
        "reviewer_comment": "   "
    }
    response = client.post("/api/reviews", json=review_payload)
    assert response.status_code == 422

def test_review_nonexistent_case_returns_404(client: TestClient):
    review_payload = {
        "case_id": 99999,
        "status": "ACCEPTED",
        "reviewer_name": "Engineer",
        "reviewer_comment": "Test"
    }
    response = client.post("/api/reviews", json=review_payload)
    assert response.status_code == 404
