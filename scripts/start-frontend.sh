#!/usr/bin/env bash
# ============================================
#  NetSage AI - Start Frontend (Vite)
# ============================================
set -e
cd "$(dirname "$0")/../frontend"

if [ ! -d node_modules ]; then
    echo "[NetSage] Installing npm dependencies (first run only)..."
    npm install
fi

if [ ! -f .env ]; then
    echo "[NetSage] Creating .env from .env.example..."
    cp .env.example .env
fi

echo "[NetSage] Starting frontend on http://localhost:5173"
npm run dev