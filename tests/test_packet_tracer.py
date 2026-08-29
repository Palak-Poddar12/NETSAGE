import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.services.packet_tracer_service import packet_tracer_service
from app.schemas.packet_tracer import (
    PacketTracerCommandEvidence,
    PacketTracerCaseEvidence,
    CommandOutputItem,
    PacketTracerFileImportRequest,
    PacketTracerVerificationRequest
)

def test_evidence_upload_and_retrieval(client: TestClient):
    payload = {
        "case_id": "NET-101",
        "device": "SW1",
        "command": "show vlan brief",
        "output": "1   default   active  Gi0/1\n10  Users     active  Gi0/2"
    }
    # 1. Upload single command evidence
    res = client.post("/api/packet-tracer/evidence", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["success"] is True
    assert data["case_id"] == "NET-101"
    assert data["device"] == "SW1"
    assert data["command"] == "show vlan brief"

    # 2. Upload second command evidence for same case
    payload2 = {
        "case_id": "NET-101",
        "device": "R1",
        "command": "show ip route",
        "output": "C 192.168.1.0/24 is directly connected, Gig0/0"
    }
    res2 = client.post("/api/packet-tracer/evidence", json=payload2)
    assert res2.status_code == 201

    # 3. Retrieve all evidence for case
    get_res = client.get("/api/packet-tracer/evidence/NET-101")
    assert get_res.status_code == 200
    evidence_list = get_res.json()
    assert evidence_list["case_id"] == "NET-101"
    assert evidence_list["total_items"] == 2
    assert len(evidence_list["evidence"]) == 2
    devices = {e["device"] for e in evidence_list["evidence"]}
    assert devices == {"SW1", "R1"}

def test_empty_output_rejection_validation(client: TestClient):
    # Empty string output
    payload = {
        "case_id": "NET-102",
        "device": "SW1",
        "command": "show vlan brief",
        "output": "   "
    }
    res = client.post("/api/packet-tracer/evidence", json=payload)
    assert res.status_code == 422

def test_malformed_evidence_rejected(client: TestClient):
    # Missing command
    payload = {
        "case_id": "NET-103",
        "device": "SW1",
        "output": "Some output"
    }
    res = client.post("/api/packet-tracer/evidence", json=payload)
    assert res.status_code == 422

def test_import_txt_cli_transcript(client: TestClient):
    txt_content = """
SW1# show vlan brief
1    default                          active    Fa0/1, Fa0/2
10   Engineering                      active    Fa0/3
20   Marketing                        active    Fa0/4

SW1# show interfaces trunk
Port        Mode         Encapsulation  Status        Native vlan
Gig0/1      on           802.1q         trunking      1

R1# show ip interface brief
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0     192.168.1.1     YES manual up                    up
GigabitEthernet0/1     10.0.0.1        YES manual administratively down down
"""
    req = {
        "case_id": "NET-TXT-01",
        "file_format": "txt",
        "content": txt_content,
        "title": "Branch Office Switch Fault",
        "symptom": "Engineering team cannot reach router"
    }
    res = client.post("/api/packet-tracer/import-file", json=req)
    assert res.status_code == 201
    data = res.json()
    assert data["success"] is True
    assert data["imported_commands_count"] == 3
    assert "SW1" in data["devices"]
    assert "R1" in data["devices"]

    # Verify retrieval
    ev_res = client.get("/api/packet-tracer/evidence/NET-TXT-01")
    assert ev_res.status_code == 200
    assert ev_res.json()["total_items"] == 3

def test_import_csv_evidence(client: TestClient):
    csv_content = """device,command,output
SW1,show vlan brief,"1 default active Gi0/1\n10 Users active Gi0/2"
R1,show ip route,"S* 0.0.0.0/0 [1/0] via 10.0.0.1"
"""
    req = {
        "case_id": "NET-CSV-01",
        "file_format": "csv",
        "content": csv_content
    }
    res = client.post("/api/packet-tracer/import-file", json=req)
    assert res.status_code == 201
    data = res.json()
    assert data["success"] is True
    assert data["imported_commands_count"] == 2

def test_packet_tracer_bundle_and_rule_engine_integration(client: TestClient):
    bundle_payload = {
        "case_id": "NET-BUNDLE-01",
        "source": "Cisco Packet Tracer",
        "title": "VLAN Isolation Problem",
        "symptom": "PC1 in VLAN 30 cannot reach Core Gateway",
        "topology": {
            "devices": [{"name": "PC1"}, {"name": "SW1"}, {"name": "R1"}],
            "links": [{"source": "PC1", "target": "SW1"}]
        },
        "addressing": [
            {"device": "PC1", "interface": "eth0", "ip_address": "192.168.30.10", "subnet_mask": "255.255.255.0", "vlan": 30, "default_gateway": "192.168.30.1"}
        ],
        "show_outputs": [
            {
                "device": "SW1",
                "command": "show vlan brief",
                "output": "1   default   active  Gi0/1\n10  Users     active  Gi0/2\n20  Voice     active  Gi0/3"
            },
            {
                "device": "R1",
                "command": "show ip interface brief",
                "output": "Gig0/0.30  192.168.30.1  YES manual up up"
            }
        ],
        "notes": "Collected during troubleshooting session"
    }

    res = client.post("/api/packet-tracer/bundle", json=bundle_payload)
    assert res.status_code == 201
    case_detail = res.json()

    # Rule Engine must detect missing VLAN 30 on SW1
    findings = case_detail["rule_findings"]
    missing_vlan_finding = next((f for f in findings if f["rule_id"] == "missing_vlan"), None)
    assert missing_vlan_finding is not None
    assert missing_vlan_finding["passed"] is False
    assert "VLAN 30" in missing_vlan_finding["details"]

    # AI Diagnosis must ground itself in evidence
    diag = case_detail["diagnosis"]
    assert diag["confidence"] >= 0.8
    assert "vlan 30" in diag["root_cause"].lower() or "missing" in diag["root_cause"].lower()
    assert not diag["is_insufficient_evidence"]

def test_insufficient_evidence_when_telemetry_missing(client: TestClient):
    # Upload only a non-diagnostic comment or empty case
    empty_bundle = {
        "case_id": "NET-EMPTY-01",
        "title": "Mystery failure",
        "symptom": "Network is slow",
        "show_outputs": []
    }
    res = client.post("/api/packet-tracer/bundle", json=empty_bundle)
    assert res.status_code == 201
    diag = res.json()["diagnosis"]
    assert diag["is_insufficient_evidence"] is True
    assert "insufficient" in diag["root_cause"].lower() or diag["confidence"] <= 0.6

def test_packet_tracer_verification_workflow(client: TestClient):
    # 1. Create a case with an interface down fault
    initial_bundle = {
        "case_id": "NET-VERIFY-01",
        "title": "Server Interface Down",
        "symptom": "Database Server is unreachable",
        "topology": {"devices": [{"name": "R1"}]},
        "addressing": [{"device": "R1", "interface": "Gig0/1", "ip_address": "10.0.1.1"}],
        "show_outputs": [
            {
                "device": "R1",
                "command": "show ip interface brief",
                "output": "GigabitEthernet0/1 10.0.1.1 YES manual administratively down down"
            }
        ]
    }
    client.post("/api/packet-tracer/bundle", json=initial_bundle)

    # 2. Human engineer fixes network in Packet Tracer (executes 'no shutdown')
    # and runs verification command 'show ip interface brief' and ping test
    verify_payload = {
        "case_id": "NET-VERIFY-01",
        "verification_outputs": [
            {
                "device": "R1",
                "command": "show ip interface brief",
                "output": "GigabitEthernet0/1 10.0.1.1 YES manual up up"
            },
            {
                "device": "R1",
                "command": "ping 10.0.1.100",
                "output": "Sending 5, 100-byte ICMP Echos to 10.0.1.100, timeout is 2 seconds:\n!!!!!\nSuccess rate is 100 percent (5/5), round-trip min/avg/max = 1/2/4 ms"
            }
        ],
        "notes": "Interface un-shut and verified 100% ping reachability."
    }

    verify_res = client.post("/api/packet-tracer/verify/NET-VERIFY-01", json=verify_payload)
    assert verify_res.status_code == 200
    v_data = verify_res.json()
    assert v_data["is_resolved"] is True
    assert v_data["status"] == "VERIFIED"
    assert "All 10 deterministic network rules passed" in v_data["summary"]

    # Verify that case status in DB is now VERIFIED
    case_db_res = client.get("/api/packet-tracer/evidence/NET-VERIFY-01")
    assert case_db_res.status_code == 200
    # Verification outputs are marked with is_verification=True
    ev_items = case_db_res.json()["evidence"]
    assert any(e["is_verification"] is True for e in ev_items)

def test_packet_tracer_verification_fails_if_fault_remains(client: TestClient):
    # Create case
    initial_bundle = {
        "case_id": "NET-VERIFY-02",
        "title": "Unfixed Fault",
        "symptom": "Duplicate IP problem",
        "addressing": [
            {"device": "H1", "ip_address": "192.168.1.50"},
            {"device": "H2", "ip_address": "192.168.1.50"}
        ],
        "show_outputs": []
    }
    client.post("/api/packet-tracer/bundle", json=initial_bundle)

    # Verification attempt without fixing addressing
    verify_payload = {
        "case_id": "NET-VERIFY-02",
        "verification_outputs": [
            {
                "device": "H1",
                "command": "ping 192.168.1.50",
                "output": "Success rate is 0 percent (0/5)"
            }
        ]
    }
    verify_res = client.post("/api/packet-tracer/verify/NET-VERIFY-02", json=verify_payload)
    assert verify_res.status_code == 200
    v_data = verify_res.json()
    assert v_data["is_resolved"] is False
    assert v_data["status"] == "UNRESOLVED"
    assert "Remaining faults detected" in v_data["summary"]
