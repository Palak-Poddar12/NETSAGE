import pytest
from fastapi.testclient import TestClient

def test_create_case_endpoint(client: TestClient, sample_case_payload: dict):
    response = client.post("/api/cases", json=sample_case_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["title"] == sample_case_payload["title"]
    assert data["status"] == "DIAGNOSED"
    assert "diagnosis" in data
    assert data["diagnosis"]["root_cause"] is not None
    assert "rule_findings" in data
    assert len(data["rule_findings"]) == 10
    assert "correlation" in data
    assert "evaluation" in data
    assert data["review"] is None

def test_list_cases_endpoint(client: TestClient, sample_case_payload: dict):
    # Create 2 cases
    client.post("/api/cases", json=sample_case_payload)
    sample_case_payload["title"] = "Case 2"
    client.post("/api/cases", json=sample_case_payload)

    response = client.get("/api/cases")
    assert response.status_code == 200
    cases = response.json()
    assert len(cases) == 2
    assert cases[0]["title"] in ["Case 2", "Branch Office connectivity loss to Core Switch"]

def test_get_case_by_id_endpoint(client: TestClient, sample_case_payload: dict):
    res = client.post("/api/cases", json=sample_case_payload)
    case_id = res.json()["id"]

    get_res = client.get(f"/api/cases/{case_id}")
    assert get_res.status_code == 200
    case_detail = get_res.json()
    assert case_detail["id"] == case_id
    assert case_detail["diagnosis"]["id"] is not None

def test_get_nonexistent_case_returns_404(client: TestClient):
    response = client.get("/api/cases/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_create_case_missing_fields_returns_422(client: TestClient):
    response = client.post("/api/cases", json={"title": ""})
    assert response.status_code == 422
