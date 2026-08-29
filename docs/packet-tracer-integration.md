# Cisco Packet Tracer Integration Guide

This document defines the architecture, evidence collection procedures, verification workflows, and operating model for integrating Cisco Packet Tracer with NetSage AI.

---

## 1. Executive Overview

| System | Role | Scope & Capabilities |
|---|---|---|
| **Cisco Packet Tracer** | Network Simulation & Reproduction | Simulates Cisco IOS routers, Catalyst switches, end hosts, routing protocols (OSPF, EIGRP, BGP), VLANs, ACLs, NAT, DHCP, and physical link states. Acts as the execution ground for reproducing network faults. |
| **NetSage AI** | Intelligent Diagnostic & Reasoning Engine | Ingests Cisco show command outputs and addressing telemetry, executes 10 deterministic network rules, coordinates AI diagnostic reasoning, performs evidence correlation, and guides human verification. |

---

## 2. Evidence Movement Architecture

NetSage AI integrates with Cisco Packet Tracer through an **Evidence-First Architecture**. Rather than assuming direct programmatic control over Packet Tracer, NetSage consumes authentic Cisco CLI outputs captured from the simulated devices.

```
┌─────────────────────────────────────────────────────────────┐
│                 Cisco Packet Tracer                         │
│  (Simulates network topology, interfaces, routing, ACLs)    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               │  1. Human runs show commands
                               │  2. Copies CLI outputs
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 NetSage Evidence Ingestion                  │
│  • Direct API (POST /api/packet-tracer/evidence)            │
│  • Multi-device Case Bundles (POST /api/packet-tracer/bundle)│
│  • CLI Transcript / CSV File Import (/import-file)          │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              Deterministic Rule Engine (10 Rules)           │
│  (Evaluates Duplicate IP, Subnets, Gateways, Down Links,   │
│   Missing VLANs, Trunk Mismatches, Missing Routes, ACLs)    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   AI Diagnostic Reasoning                   │
│  (Grounded root-cause analysis citing verified evidence)    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Evidence Correlation Engine                 │
│  (Detects agreements, conflicts, hallucinations, gaps)      │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Human Review & Manual Fix                   │
│  (Engineer applies verified remediation in Packet Tracer)   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Post-Fix Telemetry Verification             │
│  (Re-runs verification show/ping commands to confirm state) │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Supported Evidence Ingestion Formats

NetSage provides three flexible methods for importing Packet Tracer telemetry:

### 3.1 Single Command Evidence Upload
- **Endpoint**: `POST /api/packet-tracer/evidence`
- **Payload**:
```json
{
  "case_id": "NET-001",
  "device": "SW1",
  "command": "show vlan brief",
  "output": "1    default    active    Gi0/1\n10   Users      active    Gi0/2"
}
```

### 3.2 Full Case Evidence Bundle
- **Endpoint**: `POST /api/packet-tracer/bundle`
- **Payload**:
```json
{
  "case_id": "NET-001",
  "source": "Cisco Packet Tracer",
  "title": "VLAN 30 Isolation",
  "symptom": "Finance host cannot ping default gateway",
  "topology": {
    "devices": [{"name": "PC1"}, {"name": "SW1"}, {"name": "R1"}],
    "links": [{"source": "PC1", "target": "SW1"}, {"source": "SW1", "target": "R1"}]
  },
  "addressing": [
    {
      "device": "PC1",
      "interface": "eth0",
      "ip_address": "192.168.30.50",
      "subnet_mask": "255.255.255.0",
      "default_gateway": "192.168.30.1",
      "vlan": 30
    }
  ],
  "show_outputs": [
    {
      "device": "SW1",
      "command": "show vlan brief",
      "output": "1   default   active  Gi0/1\n10  Users     active  Gi0/2"
    },
    {
      "device": "R1",
      "command": "show ip route",
      "output": "C 192.168.30.0/24 is directly connected, GigabitEthernet0/0.30"
    }
  ],
  "notes": "Troubleshooting session ticket #1042"
}
```

### 3.3 Raw CLI Transcript (.txt) & CSV File Import
- **Endpoint**: `POST /api/packet-tracer/import-file`
- **Transcript Format Example**:
```text
SW1# show vlan brief
1    default                          active    Gi0/1
10   Engineering                      active    Gi0/2

R1# show ip interface brief
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0     192.168.1.1     YES manual up                    up
GigabitEthernet0/1     10.0.0.1        YES manual administratively down down
```

---

## 4. End-to-End Troubleshooting & Verification Workflow

1. **Build & Reproduce**: Recreate the reported network topology and fault inside Cisco Packet Tracer.
2. **Collect Show Outputs**: Run key diagnostic commands (`show ip interface brief`, `show vlan brief`, `show interfaces trunk`, `show ip route`, `show access-lists`, `show running-config`).
3. **Import Telemetry**: Upload evidence to NetSage via API, transcript import, or the dashboard.
4. **Automated Analysis**: NetSage runs the 10 deterministic network rules and AI diagnostic engine.
5. **Review Diagnosis**: The human engineer reviews the identified root cause, cited evidence, and proposed remediation.
6. **Apply Fix**: The engineer enters configuration mode in Packet Tracer to apply the fix (e.g. `vlan 30`, `no shutdown`, `switchport trunk allowed vlan add 30`).
7. **Verification Telemetry**: The engineer runs post-fix verification commands (`ping`, `show ip interface brief`) and submits them to `POST /api/packet-tracer/verify/{case_id}`.
8. **Confirmation**: NetSage validates that all deterministic rules now pass and marks the case as `VERIFIED`.

---

## 5. Automation vs. Human Responsibility Matrix

| Action | Automated by NetSage AI | Requires Human Action |
|---|:---:|:---:|
| Topology simulation execution | | Yes (Packet Tracer) |
| Running initial show commands | | Yes (Packet Tracer CLI) |
| Ingestion & command output parsing | Yes | |
| 10 Deterministic networking checks | Yes | |
| Grounded AI root-cause diagnosis | Yes | |
| Evidence correlation & hallucination check | Yes | |
| Applying configuration changes | | Yes (Safety guarantee) |
| Running post-fix verification commands | | Yes (Packet Tracer CLI) |
| Re-evaluating rules & certifying resolution | Yes | |

---

## 6. Current Limitations & Future Extensibility

### Current Limitations
- **No Direct Socket / Live API Injection**: Cisco Packet Tracer does not expose an official standard REST API. NetSage intentionally avoids unofficial hacks or simulated socket hooks to guarantee deterministic safety.
- **Evidence Completeness**: NetSage relies on the commands provided by the engineer; if critical commands are omitted, NetSage flags `is_insufficient_evidence: true` and recommends the exact command to run next.

### Future Extensibility
- **Extensible Emulator Connectors**: The service architecture is designed modularly. Connectors for EVE-NG, GNS3, Containerlab, and Cisco CML (Cisco Modeling Labs REST API) can plug directly into the existing `PacketTracerService` ingestion pipeline without changing rule or AI diagnostic engines.
