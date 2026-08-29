import pytest
from fastapi.testclient import TestClient

def test_full_end_to_end_pipeline(client: TestClient):
    # 1. Create a complex network case with interface down and gateway mismatch
    case_payload = {
        "title": "Total Outage in Building 4",
        "symptom": "Finance department workstations cannot access ERP server or the Internet.",
        "topology": {
            "devices": [
                {"name": "Host-Fin-1", "type": "host"},
                {"name": "SW-Bldg4", "type": "switch"},
                {"name": "R-Gateway", "type": "router"}
            ],
            "links": [
                {"source": "Host-Fin-1", "source_interface": "eth0", "target": "SW-Bldg4", "target_interface": "Gig0/5"},
                {"source": "SW-Bldg4", "source_interface": "Gig0/1", "target": "R-Gateway", "target_interface": "Gig0/0"}
            ]
        },
        "addressing": [
            {
                "device": "Host-Fin-1",
                "interface": "eth0",
                "ip_address": "10.4.1.50",
                "subnet_mask": "255.255.255.0",
                "default_gateway": "10.4.1.1",
                "vlan": 40
            },
            {
                "device": "R-Gateway",
                "interface": "Gig0/0",
                "ip_address": "10.4.1.1",
                "subnet_mask": "255.255.255.0",
                "default_gateway": None
            }
        ],
        "show_outputs": {
            "SW-Bldg4": {
                "show_interfaces_status": "Gig0/5   connected    40         a-full  a-1000 10/100/1000BaseTX\nGig0/1   disabled     trunk      a-full  a-1000 10/100/1000BaseTX",
                "show_vlan_brief": "40   Finance                          active    Gig0/5"
            },
            "R-Gateway": {
                "show_ip_interface_brief": "Gig0/0                10.4.1.1        YES manual administratively down down",
                "show_ip_route": "C 10.4.1.0/24 is directly connected, GigabitEthernet0/0"
            }
        }
    }

    # Step 1: POST /api/cases
    create_res = client.post("/api/cases", json=case_payload)
    assert create_res.status_code == 201
    case_data = create_res.json()
    case_id = case_data["id"]
    assert case_data["status"] == "DIAGNOSED"

    # Verify rule findings detected interface down
    findings = case_data["rule_findings"]
    assert len(findings) == 10
    intf_down_finding = next(f for f in findings if f["rule_id"] == "interface_down")
    assert intf_down_finding["passed"] is False
    assert "administratively down" in intf_down_finding["details"] or "disabled" in intf_down_finding["details"]

    # Verify AI diagnosis
    diag = case_data["diagnosis"]
    assert diag["confidence"] > 0.7
    assert diag["is_insufficient_evidence"] is False
    assert "down" in diag["root_cause"].lower()

    # Verify Evidence Correlation
    corr = case_data["correlation"]
    assert corr["agreement"] is True
    assert corr["conflict"] is False

    # Verify Evaluation
    eval_data = case_data["evaluation"]
    assert eval_data["root_cause_correctness"] >= 0.9
    assert eval_data["next_command_quality"] == "HIGH"
    assert eval_data["proposed_fix_safety"] == "SAFE"

    # Step 2: GET /api/cases/{id}
    get_res = client.get(f"/api/cases/{case_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == case_id

    # Step 3: GET /api/cases (listing)
    list_res = client.get("/api/cases")
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # Step 4: POST /api/reviews (Submit Human Review)
    review_res = client.post("/api/reviews", json={
        "case_id": case_id,
        "status": "ACCEPTED",
        "reviewer_name": "Tier 3 Escalation Engineer",
        "reviewer_comment": "Confirmed that R-Gateway Gig0/0 was administratively shut down during maintenance window."
    })
    assert review_res.status_code == 201
    assert review_res.json()["status"] == "ACCEPTED"

    # Verify case status transitioned to ACCEPTED
    updated_case = client.get(f"/api/cases/{case_id}").json()
    assert updated_case["status"] == "ACCEPTED"
    assert updated_case["review"] is not None
    assert updated_case["diagnosis"] is not None

    # Step 5: GET /api/dashboard/metrics
    metrics_res = client.get("/api/dashboard/metrics")
    assert metrics_res.status_code == 200
    metrics = metrics_res.json()
    assert metrics["total_cases"] >= 1
    assert metrics["reviews"]["accepted"] >= 1
