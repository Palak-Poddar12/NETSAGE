@echo off
REM ============================================
REM  NetSage AI - Start Frontend (Vite)
REM ============================================
cd /d "%~dp0..\frontend"

if not exist node_modules (
    echo [NetSage] Installing npm dependencies (first run only)...
    call npm install
    if errorlevel 1 (
        echo [NetSage] ERROR: npm install failed. Make sure Node.js 18+ is installed.
        pause
        exit /b 1
    )
)

if not exist .env (
    echo [NetSage] Creating .env from .env.example...
    copy .env.example .env >nul
)

echo [NetSage] Starting frontend on http://localhost:5173
call npm run dev