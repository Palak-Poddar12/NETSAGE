# NetSage AI — Frontend

React 18 + Vite + Tailwind CSS dashboard for NetSage AI: case intake, diagnosis viewer, human review workflow, and live metrics.

## Tech Stack
- **React 18** + **React Router 6**
- **Vite 5** — dev server & build tool (with `/api` proxy to the backend)
- **Tailwind CSS 3** — styling (Cisco NetAcad-inspired theme, dark mode)
- **Recharts** — dashboard charts
- **lucide-react** — icons

## Setup

```bash
cd frontend
npm install
copy .env.example .env        # cp .env.example .env on Unix
npm run dev
```

Open **http://localhost:5173**.

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `VITE_API_URL` | *(empty)* | Leave empty in development — Vite proxies `/api/*` to `http://127.0.0.1:8000`. Set a full URL to target a remote backend. |

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start dev server on port 5173 |
| `npm run build` | Production build to `dist/` |
| `npm run preview` | Preview the production build locally |

## Backend Connection

- The dev server proxies `/api/*` → `http://127.0.0.1:8000` (see `vite.config.js`), so no CORS configuration is needed locally.
- `src/services/api.js` contains the API client. If the backend is unreachable, dev fallback (mock) data is shown and marked in the console — start the backend for live data.
- The sidebar/topbar connection indicator polls `GET /api/health` every 15 seconds.

## Pages

| Route | Page |
|-------|------|
| `/dashboard` | Live metrics, severity distribution, recent findings |
| `/cases` | Case list (card/table views, search & filters) |
| `/cases/:caseId` | Case detail / diagnosis |
| `/new-case` | Create a new diagnostic case |
| `/diagnosis/:diagnosisId` | Full diagnosis workspace (evidence, rules, AI) |
| `/review/:diagnosisId` | Human review (ACCEPTED / EDITED / REJECTED) |
