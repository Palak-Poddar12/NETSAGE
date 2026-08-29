# NetSage AI

NetSage AI is an enterprise-grade **autonomous network troubleshooting platform** for Cisco environments — a FastAPI backend (deterministic rule engine + AI diagnostics) paired with a React dashboard frontend (cases, diagnosis review, human-in-the-loop workflow).

---

## Project Structure

```
NETSAGE/
├── backend/                    # FastAPI backend (Python)
│   ├── app/
│   │   ├── main.py             # FastAPI entrypoint, CORS, middleware
│   │   ├── config.py           # Environment settings (.env)
│   │   ├── database.py         # SQLAlchemy engine & session
│   │   ├── api/                # Route controllers (cases, diagnoses, reviews, dashboard, health, packet-tracer)
│   │   ├── models/             # DB models (Case, Diagnosis, Evaluation, Review)
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   ├── rules/              # 10 deterministic networking rules + engine
│   │   └── services/           # Business logic (case, AI, correlation, evaluation, review, dashboard)
│   ├── tests/                  # Pytest suite (unit, API, rule & integration tests)
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
├── frontend/                   # React 18 + Vite + Tailwind CSS dashboard
│   ├── public/                 # Static assets (favicon.svg)
│   ├── src/
│   │   ├── components/         # UI components
│   │   ├── pages/              # Dashboard, Cases, NewCase, Diagnosis, HumanReview
│   │   ├── context/            # CaseContext, ThemeContext
│   │   ├── services/           # API client (api.js, mockData.js dev fallback)
│   │   ├── hooks/              # useApi, useHealth
│   │   └── utils/              # constants, formatters
│   ├── index.html
│   ├── vite.config.js          # Dev server with /api proxy to backend
│   ├── package.json
│   ├── .env.example
│   └── README.md
├── docs/                       # API contract & Packet Tracer integration docs
├── scripts/                    # One-click run scripts (Windows .bat / Linux .sh)
├── SETUP.md                    # Full step-by-step setup & troubleshooting guide
└── README.md
```

---

## Quick Start (One Click)

**Windows:** double-click or run:
```bat
scripts\start-dev.bat
```

**Linux / macOS:**
```bash
chmod +x scripts/*.sh
./scripts/start-dev.sh
```

This installs everything on first run, then starts:
| Service  | URL                              |
|----------|----------------------------------|
| Frontend | http://localhost:5173            |
| Backend  | http://127.0.0.1:8000            |
| API Docs | http://127.0.0.1:8000/docs       |

> **Prerequisites:** Python 3.11+ and Node.js 18+

---

## Manual Setup

### 1. Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows   (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env          # Linux/macOS: cp .env.example .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 2. Frontend (new terminal)
```bash
cd frontend
npm install
copy .env.example .env          # Linux/macOS: cp .env.example .env
npm run dev
```

Open **http://localhost:5173** — the Vite dev server proxies all `/api/*` calls to the backend, so no CORS setup is needed.

---

## Testing

```bash
# Backend test suite (from backend/ with venv active)
pytest -v --tb=short

# Frontend production build check (from frontend/)
npm run build
```

---

## Key Features

1. **Deterministic Network Rule Engine** — 10 networking rules (`duplicate_ip`, `invalid_subnet`, `gateway_mismatch`, `interface_down`, `missing_vlan`, `trunk_vlan_mismatch`, `missing_route`, `acl_deny`, `dhcp_inconsistency`, `nat_inconsistency`) evaluated with Python's native `ipaddress` library.
2. **AI Diagnostic Service** — grounded root-cause analysis with anti-hallucination constraints; deterministic offline fallback when no `OPENAI_API_KEY` is set.
3. **Evidence Correlation Engine** — agreement / conflict / unsupported-claim / hallucination detection.
4. **Automated AI Evaluation** — multi-dimensional scoring of every diagnosis.
5. **Human Review Workflow** — `ACCEPTED` / `EDITED` / `REJECTED` verdicts with strict schema validation.
6. **Dynamic Dashboard Metrics** — calculated live from database records, never hardcoded.
7. **Cisco Packet Tracer Integration** — import CLI transcripts (TXT/CSV/JSON), diagnose imported evidence, verify fixes.

---

## Documentation

- [`SETUP.md`](SETUP.md) — detailed setup steps, environment variables & troubleshooting
- [`docs/api-contract.md`](docs/api-contract.md) — REST API contract
- [`docs/packet-tracer-integration.md`](docs/packet-tracer-integration.md) — Packet Tracer integration guide
- [`backend/README.md`](backend/README.md) / [`frontend/README.md`](frontend/README.md) — per-app details

