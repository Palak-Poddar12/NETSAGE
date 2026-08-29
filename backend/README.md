# NetSage AI — Backend

FastAPI backend for the NetSage AI network troubleshooting platform: deterministic rule engine, AI diagnostics, evidence correlation, automated evaluation, and human review workflow.

## Tech Stack
- **FastAPI** + **Uvicorn** — REST API
- **SQLAlchemy 2.0** + **SQLite** — persistence
- **Pydantic v2** — request/response validation
- **OpenAI SDK (optional)** — LLM diagnosis with deterministic offline fallback
- **Pytest** — test suite

## Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate              # Windows  (source .venv/bin/activate on Unix)
pip install -r requirements.txt
copy .env.example .env              # cp .env.example .env on Unix
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Root health: http://127.0.0.1:8000/health
- API health (used by frontend): http://127.0.0.1:8000/api/health

## API Endpoints (prefix `/api`)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/health` | Health probe with DB status (frontend polls this) |
| `POST` | `/api/cases` | Create case + run full diagnostic pipeline |
| `GET` | `/api/cases` | List case summaries (`?status=&limit=&offset=`) |
| `GET` | `/api/cases/{case_id}` | Full case detail (diagnosis, findings, evaluation, review) |
| `POST` | `/api/diagnose` | Get diagnostic bundle for an existing case (`{"case_id": n}`) |
| `GET` | `/api/diagnoses/{diagnosis_id}` | Fetch a single stored diagnosis |
| `POST` | `/api/reviews` | Submit human review (`ACCEPTED`/`EDITED`/`REJECTED`) |
| `GET` | `/api/dashboard/metrics` | Live aggregated metrics |
| `POST` | `/api/packet-tracer/evidence` | Upload command evidence |
| `GET` | `/api/packet-tracer/evidence/{case_id}` | List evidence for a case |
| `POST` | `/api/packet-tracer/bundle` | Import full evidence bundle |
| `POST` | `/api/packet-tracer/import-file` | Import TXT/CSV/JSON CLI transcript |
| `POST` | `/api/packet-tracer/diagnose/{case_id}` | Diagnose imported evidence |
| `POST` | `/api/packet-tracer/verify/{case_id}` | Verify post-fix resolution |

Full request/response examples: [`docs/api-contract.md`](../docs/api-contract.md).

## Tests

```bash
pytest -v --tb=short
```

## Notes
- `OPENAI_API_KEY` is optional — without it, the deterministic fallback synthesis runs fully offline.
- The SQLite file `netsage.db` is auto-created at startup; delete it for a clean state.
