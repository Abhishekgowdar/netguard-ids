@echo off
REM View NetGuard IDS Database

echo ========================================
echo 📊 Viewing Database...
echo ========================================
echo.

cd /d "%~dp0"
python view_database.py

echo.
pause
