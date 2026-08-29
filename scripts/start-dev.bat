@echo off
REM ============================================
REM  NetSage AI - Start Both (Backend + Frontend)
REM ============================================
echo [NetSage] Launching backend and frontend in separate windows...

start "NetSage Backend"  cmd /k "%~dp0start-backend.bat"
timeout /t 3 /nobreak >nul
start "NetSage Frontend" cmd /k "%~dp0start-frontend.bat"

echo.
echo   NetSage AI is starting:
echo     Backend  : http://127.0.0.1:8000  (docs at /docs)
echo     Frontend : http://localhost:5173
echo.
echo   Close the opened windows to stop the services.