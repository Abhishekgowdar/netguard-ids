@echo off
REM Start NetGuard IDS Frontend Server
REM This runs in the background and opens Chrome automatically

echo ========================================
echo Starting NetGuard IDS Frontend...
echo ========================================

cd /d "%~dp0"

REM Start server in the background (minimized window)
start /min "NetGuard Frontend" python server.py

echo.
echo ✅ Frontend server started!
echo 🌐 Dashboard: http://localhost:3000
echo.
echo To stop: Close the "NetGuard Frontend" window
echo ========================================

timeout /t 3 >nul
