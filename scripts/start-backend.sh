#!/usr/bin/env bash
# ============================================
#  NetSage AI - Start Backend (FastAPI)
# ============================================
set -e
cd "$(dirname "$0")/../backend"

if [ ! -d .venv ]; then
    echo "[NetSage] Creating Python virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

if [ ! -f .venv/.deps_installed ]; then
    echo "[NetSage] Installing Python dependencies..."
    pip install -r requirements.txt
    touch .venv/.deps_installed
fi

if [ ! -f .env ]; then
    echo "[NetSage] Creating .env from .env.example..."
    cp .env.example .env
fi

echo "[NetSage] Starting backend on http://127.0.0.1:8000  (API docs: /docs)"
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000