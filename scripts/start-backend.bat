@echo off
REM ============================================
REM  NetSage AI - Start Backend (FastAPI)
REM ============================================
cd /d "%~dp0..\backend"

if not exist .venv (
    echo [NetSage] Creating Python virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo [NetSage] ERROR: Python not found. Install Python 3.11+ and try again.
        pause
        exit /b 1
    )
)

call .venv\Scripts\activate.bat

if not exist .venv\.deps_installed (
    echo [NetSage] Installing Python dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [NetSage] ERROR: pip install failed.
        pause
        exit /b 1
    )
    type nul > .venv\.deps_installed
)

if not exist .env (
    echo [NetSage] Creating .env from .env.example...
    copy .env.example .env >nul
)

echo [NetSage] Starting backend on http://127.0.0.1:8000  (API docs: /docs)
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000