# NetSage AI — Setup Guide (Step by Step)

This is the complete missing-steps guide: from a fresh clone to a fully running application.

---

## Step 0 — Prerequisites

| Tool | Version | Check command | Download |
|------|---------|---------------|----------|
| Python | 3.11+ (3.12/3.13/3.14 supported) | `python --version` | https://www.python.org/downloads/ |
| Node.js | 18+ | `node --version` | https://nodejs.org/ |
| npm | 9+ (ships with Node) | `npm --version` | — |
| Git | any recent | `git --version` | https://git-scm.com/ |

> On Windows, tick **"Add Python to PATH"** during Python installation.

---

## Step 1 — Get the project

```bash
git clone https://github.com/Palak-Poddar12/NETSAGE.git
cd NETSAGE
```

---

## Step 2 — Backend setup (`backend/`)

### 2.1 Create a virtual environment (recommended)
```bash
cd backend
python -m venv .venv
```

### 2.2 Activate it
- **Windows (cmd/PowerShell):** `.venv\Scripts\activate`
- **Linux/macOS:** `source .venv/bin/activate`

### 2.3 Install Python dependencies
```bash
pip install -r requirements.txt
```

Installs: `fastapi`, `uvicorn`, `pydantic`, `sqlalchemy`, `openai`, `python-dotenv`, `httpx`, `pytest`.

### 2.4 Configure environment variables
```bash
copy .env.example .env        # Windows
cp .env.example .env          # Linux/macOS
```

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `APP_NAME` | no | `NetSage AI Backend` | Service name shown in API docs |
| `DEBUG` | no | `True` | Debug mode |
| `DATABASE_URL` | no | `sqlite:///./netsage.db` | SQLAlchemy DB URL (SQLite by default) |
| `OPENAI_API_KEY` | **no** | *(empty)* | Optional LLM key — without it the deterministic offline fallback is used |
| `OPENAI_MODEL` | no | `gpt-4o-mini` | Model used when a key is provided |
| `CORS_ORIGINS` | no | localhost:5173/3000 | JSON array **or** comma-separated frontend origins |

> The app **runs fully offline without any API key** — the AI service falls back to deterministic synthesis.

### 2.5 Start the backend
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Verify:
- Health: http://127.0.0.1:8000/health → `{"status": "healthy"}`
- API health: http://127.0.0.1:8000/api/health
- Swagger docs: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

On first start the SQLite database (`backend/netsage.db`) is created automatically.

---

## Step 3 — Frontend setup (`frontend/`) — *new terminal*

### 3.1 Install npm dependencies
```bash
cd frontend
npm install
```

### 3.2 Configure environment variables (optional)
```bash
copy .env.example .env        # Windows
cp .env.example .env          # Linux/macOS
```

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `VITE_API_URL` | no | *(empty)* | Leave empty for dev — Vite proxies `/api/*` to `http://127.0.0.1:8000`. Set a full URL only when pointing at a remote backend. |

### 3.3 Start the dev server
```bash
npm run dev
```

Open **http://localhost:5173** — the sidebar indicator should turn green ("connected") once the backend is reachable.

---

## Step 4 — Verify the full flow

1. **Dashboard** (`/dashboard`) shows live metrics from `GET /api/dashboard/metrics` (zeros on a fresh DB).
2. **New Case** (`/new-case`) → fill symptom/topology/show-outputs → submit → runs `POST /api/cases` (full pipeline: 10 rules → AI → correlation → evaluation).
3. **Diagnosis** (`/diagnosis`) shows rule findings, evidence, and the AI diagnosis.
4. **Human Review** (`/review`) → submit `ACCEPTED` / `EDITED` / `REJECTED` → `POST /api/reviews`.
5. Dashboard metrics update live.

---

## Step 5 — Run the test suite

```bash
cd backend
.venv\Scripts\activate        # activate venv first
pytest -v --tb=short
```

Frontend production build check:
```bash
cd frontend
npm run build
```

---

## One-Click Alternative

From the project root:
- **Windows:** `scripts\start-dev.bat` (starts backend + frontend in separate windows)
- **Linux/macOS:** `./scripts/start-dev.sh`

Individual scripts: `scripts\start-backend.bat`, `scripts\start-frontend.bat` (+ `.sh` variants). They auto-create the venv, install dependencies on first run, and create `.env` from `.env.example`.

---

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| Sidebar shows "offline" | Backend not started | Start backend first (Step 2.5); frontend polls `/api/health` every 15s |
| Port 8000 already in use | Another app owns the port | `uvicorn app.main:app --reload --port 8001` and set `VITE_API_URL=http://127.0.0.1:8001` in `frontend/.env` |
| Port 5173 already in use | Another Vite instance | `npm run dev -- --port 5174` |
| CORS errors in browser console | Backend started with custom `CORS_ORIGINS` | Add your frontend origin to `CORS_ORIGINS` in `backend/.env` and restart |
| `python: command not found` | Python not on PATH | Reinstall Python with "Add to PATH", or use `py -m venv .venv` |
| Dashboard shows demo data | Backend unreachable (dev fallback engaged) | Check backend terminal for errors; refresh the page once backend is up |
| Database locked / corrupted state | Stale SQLite file | Stop backend, delete `backend/netsage.db`, restart (auto-recreated) |
| `pip install` fails on proxy networks | Corporate proxy | `pip install -r requirements.txt --proxy http://proxy:port` |

---

## Stopping the app

- `Ctrl+C` in each terminal (manual mode), or close the two windows opened by `start-dev.bat`.
- The SQLite DB and logs persist between runs; delete `backend/netsage.db` for a factory reset.
