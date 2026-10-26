@echo off
REM ============================================
REM NetGuard IDS - Complete Startup Script
REM Starts Backend + Frontend + Opens Dashboard
REM ============================================

echo ========================================
echo 🛡️  NetGuard IDS - Starting System
echo ========================================
echo.

REM Check if running as Administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Running as Administrator
) else (
    echo ⚠️  WARNING: Not running as Administrator!
    echo    Packet capture requires admin privileges.
    echo    Right-click this file and select "Run as Administrator"
    echo.
    pause
    exit /b 1
)

echo.
echo 📦 Starting Backend (Packet Capture + API)...
cd /d "%~dp0\backend"
start "NetGuard Backend" cmd /k python main.py

echo ⏳ Waiting for backend to initialize...
timeout /t 5 >nul

echo.
echo 🌐 Starting Frontend Dashboard...
cd /d "%~dp0\frontend"
start /min "NetGuard Frontend" python server.py

echo.
echo ========================================
echo ✅ NetGuard IDS Started Successfully!
echo ========================================
echo.
echo 📊 Dashboard will open automatically in Chrome
echo 🌐 URL: http://localhost:3000
echo.
echo 📁 Backend Window: "NetGuard Backend"
echo 📁 Frontend Window: "NetGuard Frontend" (minimized)
echo.
echo To stop NetGuard IDS:
echo   - Press Ctrl+C in Backend window
echo   - Close both terminal windows
echo.
echo ========================================

REM Wait a bit to let user read the message
timeout /t 3 >nul
