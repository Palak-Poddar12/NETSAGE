#!/usr/bin/env bash
# ============================================
#  NetSage AI - Start Both (Backend + Frontend)
# ============================================
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "[NetSage] Launching backend and frontend..."
bash "$SCRIPT_DIR/start-backend.sh" &
BACKEND_PID=$!
sleep 3
bash "$SCRIPT_DIR/start-frontend.sh" &
FRONTEND_PID=$!

echo ""
echo "  NetSage AI is starting:"
echo "    Backend  : http://127.0.0.1:8000  (docs at /docs)"
echo "    Frontend : http://localhost:5173"
echo ""
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait