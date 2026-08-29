# NetSage AI API Contract

This document defines the REST API contract for the NetSage AI backend.

---

## 1. Case Management Endpoints

### 1.1 Create Case and Run Diagnosis Pipeline
- **Endpoint**: `POST /api/cases`
- **Description**: Submits a new network case with symptoms, topology, addressing table, and show command outputs. Triggers the 10 deterministic networking rules, AI diagnostic service, evidence correlation engine, and automated evaluation.
- **Request Body**:
```json
{
  "title": "Branch Office connectivity loss to Core Switch",
  "symptom": "Host A (192.168.1.50) cannot ping Host B (192.168.2.50) or the default gateway.",
  "topology": {
    "devices": [
      {"name": "Host-A", "type": "host"},
      {"name": "SW-Access-1", "type": "switch"},
      {"name": "R1-Core", "type": "router"}
    ],
    "links": [
      {"source": "Host-A", "source_interface": "eth0", "target": "SW-Access-1", "target_interface": "Gig0/1"},
      {"source": "SW-Access-1", "source_interface": "Gig0/24", "target": "R1-Core", "target_interface": "Gig0/0"}
    ]
  },
  "addressing": [
    {
      "device": "Host-A",
      "interface": "eth0",
      "ip_address": "192.168.1.50",
      "subnet_mask": "255.255.255.0",
      "default_gateway": "192.168.1.1",
      "vlan": 10
    },
    {
      "device": "R1-Core",
      "interface": "Gig0/0.10",
      "ip_address": "192.168.1.1",
      "subnet_mask": "255.255.255.0",
      "default_gateway": null,
      "vlan": 10
    }
  ],
  "show_outputs": {
    "SW-Access-1": {
      "show_interfaces_status": "Gig0/1   connected    10         a-full  a-1000 10/100/1000BaseTX\nGig0/24  connected    trunk      a-full  a-1000 10/100/1000BaseTX",
      "show_vlan_brief": "10   Users                            active    Gig0/1",
      "show_interfaces_trunk": "Gig0/24  10,20,30,40"
    },
    "R1-Core": {
      "show_ip_interface_brief": "Gig0/0.10             192.168.1.1     YES manual up                    up",
      "show_ip_route": "C 192.168.1.0/24 is directly connected, GigabitEthernet0/0.10"
    }
  }
}
```

- **Response (`201 Created`)**:
```json
{
  "id": 1,
  "title": "Branch Office connectivity loss to Core Switch",
  "symptom": "Host A (192.168.1.50) cannot ping Host B (192.168.2.50) or the default gateway.",
  "status": "DIAGNOSED",
  "created_at": "2026-08-29T11:00:00Z",
  "updated_at": "2026-08-29T11:00:00Z",
  "diagnosis": {
    "id": 1,
    "root_cause": "VLAN 10 is missing or inactive on uplink trunk port.",
    "osi_layer": "Data Link (Layer 2)",
    "confidence": 0.95,
    "reasoning": "Host A is assigned to VLAN 10, but the router subinterface Gig0/0.10 encapsulation is not receiving tagged frames due to trunk misconfiguration.",
    "evidence_used": [
      "SW-Access-1 show_vlan_brief shows VLAN 10 active on Gig0/1",
      "Host-A addressing indicates VLAN 10"
    ],
    "next_diagnostic_command": "show mac address-table vlan 10",
    "proposed_fix": "Configure switchport trunk allowed vlan add 10 on Gig0/24",
    "is_insufficient_evidence": false
  },
  "rule_findings": [
    {
      "rule_id": "missing_vlan",
      "rule_name": "Missing or Inactive VLAN",
      "passed": true,
      "severity": "info",
      "details": "All access ports are assigned to active VLANs.",
      "affected_devices": [],
      "affected_interfaces": []
    }
  ],
  "correlation": {
    "agreement": true,
    "conflict": false,
    "unsupported_claims": [],
    "missing_evidence": [],
    "possible_hallucinations": [],
    "explanation": "AI diagnosis is fully grounded in the provided show command outputs and addressing table."
  },
  "evaluation": {
    "id": 1,
    "root_cause_correctness": 1.0,
    "evidence_support_score": 1.0,
    "osi_layer_match": true,
    "next_command_quality": "HIGH",
    "proposed_fix_safety": "SAFE",
    "confidence_calibration": "WELL_CALIBRATED",
    "notes": "Diagnosis correctly identifies the layer 2 fault."
  },
  "review": null
}
```

### 1.2 List All Cases
- **Endpoint**: `GET /api/cases`
- **Query Params**:
  - `status`: Optional filter (e.g. `PENDING`, `DIAGNOSED`, `ACCEPTED`, `EDITED`, `REJECTED`, `VERIFIED`)
  - `limit`: Default `50`, Max `100`
  - `offset`: Default `0`
- **Response (`200 OK`)**: Array of Case summaries.

### 1.3 Get Case by ID
- **Endpoint**: `GET /api/cases/{case_id}`
- **Response (`200 OK`)**: Full case object including `diagnosis`, `rule_findings`, `correlation`, `evaluation`, and `review`.
- **Response (`404 Not Found`)**: `{"detail": "Case {case_id} not found"}`

---

## 2. Cisco Packet Tracer Integration Endpoints

### 2.1 Upload Command Evidence
- **Endpoint**: `POST /api/packet-tracer/evidence`
- **Request Body**:
```json
{
  "case_id": "NET-001",
  "device": "SW1",
  "command": "show vlan brief",
  "output": "1   default   active   Gi0/1\n10  Users     active   Gi0/2"
}
```
- **Response (`201 Created`)**:
```json
{
  "success": true,
  "case_id": "NET-001",
  "device": "SW1",
  "command": "show vlan brief",
  "evidence_id": 1
}
```

### 2.2 Retrieve Imported Evidence for Case
- **Endpoint**: `GET /api/packet-tracer/evidence/{case_id}`
- **Response (`200 OK`)**:
```json
{
  "case_id": "NET-001",
  "total_items": 1,
  "evidence": [
    {
      "id": 1,
      "case_id": 1,
      "pt_case_id": "NET-001",
      "device": "SW1",
      "command": "show vlan brief",
      "output": "1   default   active   Gi0/1\n10  Users     active   Gi0/2",
      "is_verification": false,
      "created_at": "2026-08-29T12:00:00Z"
    }
  ]
}
```

### 2.3 Import File (TXT CLI transcript, CSV, JSON)
- **Endpoint**: `POST /api/packet-tracer/import-file`
- **Request Body**:
```json
{
  "case_id": "NET-001",
  "file_format": "txt",
  "content": "SW1# show vlan brief\n1  default active Gi0/1\nR1# show ip route\nC 192.168.1.0/24 is directly connected"
}
```
- **Response (`201 Created`)**:
```json
{
  "success": true,
  "case_id": "NET-001",
  "imported_commands_count": 2,
  "devices": ["R1", "SW1"]
}
```

### 2.4 Import Complete Case Evidence Bundle
- **Endpoint**: `POST /api/packet-tracer/bundle`
- **Request Body**: Accepts `PacketTracerCaseEvidence` schema with topology, addressing, and show outputs list.
- **Response (`201 Created`)**: `CaseDetailResponse`

### 2.5 Submit Post-Fix Verification Evidence
- **Endpoint**: `POST /api/packet-tracer/verify/{case_id}`
- **Request Body**:
```json
{
  "case_id": "NET-001",
  "verification_outputs": [
    {
      "device": "R1",
      "command": "show ip interface brief",
      "output": "Gig0/0 192.168.1.1 YES manual up up"
    },
    {
      "device": "R1",
      "command": "ping 192.168.1.50",
      "output": "Success rate is 100 percent (5/5)"
    }
  ],
  "notes": "Verified interface un-shut and ping reachability"
}
```
- **Response (`200 OK`)**:
```json
{
  "case_id": "NET-001",
  "is_resolved": true,
  "status": "VERIFIED",
  "summary": "Network resolution verified: All 10 deterministic network rules passed and verification telemetry confirms normal operation.",
  "rule_findings": [...]
}
```

---

## 3. Human Review Endpoints

### 3.1 Submit Human Review
- **Endpoint**: `POST /api/reviews`
- **Description**: Submits reviewer verdict (`ACCEPTED`, `EDITED`, or `REJECTED`). `EDITED` requires a `corrected_diagnosis` and `reviewer_comment`. `REJECTED` requires a `reviewer_comment`.
- **Request Body (ACCEPTED)**:
```json
{
  "case_id": 1,
  "status": "ACCEPTED",
  "reviewer_name": "Senior Network Engineer",
  "reviewer_comment": "Verified and approved the proposed fix."
}
```
- **Response (`201 Created`)**:
```json
{
  "id": 1,
  "case_id": 1,
  "status": "ACCEPTED",
  "reviewer_name": "Senior Network Engineer",
  "reviewer_comment": "Verified and approved the proposed fix.",
  "corrected_diagnosis": null,
  "created_at": "2026-08-29T11:05:00Z"
}
```

---

## 4. Dashboard Metrics Endpoint

### 4.1 Get Aggregated Dashboard Metrics
- **Endpoint**: `GET /api/dashboard/metrics`
- **Description**: Calculates live metrics dynamically from database tables.
- **Response (`200 OK`)**:
```json
{
  "total_cases": 25,
  "total_diagnoses": 25,
  "reviews": {
    "accepted": 18,
    "edited": 4,
    "rejected": 2,
    "pending": 1
  },
  "agreement_rate": 0.88,
  "issue_distribution": {
    "Physical / Interface (Layer 1)": 3,
    "Data Link / VLAN / Trunk (Layer 2)": 10,
    "Network / IP / Subnet (Layer 3)": 8,
    "Routing / Gateway (Layer 3)": 3,
    "Security / ACL (Layer 4)": 1
  },
  "severity_distribution": {
    "info": 4,
    "low": 6,
    "medium": 8,
    "high": 5,
    "critical": 2
  },
  "conflicts_count": 2,
  "insufficient_evidence_count": 3
}
```
