# NetSage AI Backend

NetSage AI is an enterprise-grade autonomous network troubleshooting backend engine built with FastAPI, SQLAlchemy, SQLite, Python `ipaddress`, OpenAI, and Pytest.

---

## Key Features

1. **Deterministic Network Rule Engine**:
   - Evaluates 10 fundamental networking rules using Python's native `ipaddress` library and parser heuristics without invoking an LLM for deterministic math:
     - `duplicate_ip`: Duplicate IP address conflict detection
     - `invalid_subnet`: Subnet boundary, network address, and broadcast address checks
     - `gateway_mismatch`: Default gateway subnet membership & router interface matching
     - `interface_down`: Administratively down, line protocol down, and disabled port checks
     - `missing_vlan`: Access ports configured for missing/inactive VLAN database IDs
     - `trunk_vlan_mismatch`: Native VLAN mismatch & asymmetric allowed VLAN list detection
     - `missing_route`: Destination network reachability & routing table lookup checks
     - `acl_deny`: Packet drops and matches against explicit deny access-lists
     - `dhcp_inconsistency`: DHCP pool subnet discrepancies, invalid default-routers, and conflict checks
     - `nat_inconsistency`: Missing inside/outside NAT tags and translation overload policy checks

2. **AI Diagnostic Service**:
   - Grounded root-cause analysis using provided telemetry.
   - Anti-hallucination constraints ensuring only supplied evidence is cited.
   - Resilient fallback synthesis mechanism that works seamlessly offline without external API keys.

3. **Evidence Correlation Engine**:
   - Detects agreement, conflict, unsupported claims, missing evidence, and hallucinations by cross-checking AI output against deterministic rule findings and network telemetry.

4. **Automated AI Evaluation**:
   - Multi-dimensional scoring for root-cause correctness, evidence support, OSI layer alignment, diagnostic command quality, proposed fix safety, and confidence calibration.

5. **Human Review Workflow**:
   - Supports `ACCEPTED`, `EDITED`, and `REJECTED` verdicts with strict schema validation while strictly preserving the original AI diagnosis.

6. **Dynamic Dashboard Metrics**:
   - Live metrics calculated directly from database records (never hardcoded).

---

## Directory Structure

```
netsage-backend/
├── docs/
│   └── api-contract.md             # REST API contract specification
├── app/
│   ├── main.py                     # FastAPI entrypoint, CORS, exception handlers
│   ├── config.py                   # Environment settings & secrets handling
│   ├── database.py                 # SQLAlchemy engine and session dependency
│   ├── models/                     # Database Models (Case, Diagnosis, Evaluation, Review)
│   ├── schemas/                    # Pydantic Schemas for requests and responses
│   ├── rules/                      # 10 Deterministic Networking Rules & Rule Engine
│   ├── services/                   # Business logic (Case, AI, Correlation, Evaluation, Review, Dashboard)
│   └── api/                        # API route controllers
├── tests/                          # 47 Unit, API, Rule & Integration Tests
├── .env.example
├── requirements.txt
└── README.md
```

---

## Setup & Running

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
*(Note: An `OPENAI_API_KEY` is optional; if omitted, the built-in deterministic AI synthesis handles all diagnostic reasoning safely).*

### 3. Run Development Server
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- Interactive API Docs: `http://127.0.0.1:8000/docs`
- Alternative ReDoc: `http://127.0.0.1:8000/redoc`

### 4. Run Pytest Test Suite
```bash
pytest -v --tb=short
```
