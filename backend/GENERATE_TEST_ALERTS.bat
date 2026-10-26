@echo off
REM Generate Test Alerts for NetGuard IDS Dashboard

echo ========================================
echo 🧪 Generating Test Alerts...
echo ========================================
echo.

cd /d "%~dp0"
python generate_test_alerts.py -n 20

echo.
echo ========================================
echo ✅ Test alerts generated!
echo.
echo 🌐 Open dashboard to see them:
echo    http://localhost:3000
echo ========================================
echo.

pause
