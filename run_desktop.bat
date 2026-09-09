@echo off
title Sanctum - Desktop App Mode
cd /d "%~dp0"
echo Starting Sanctum in Desktop App Mode...
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" launch_desktop_app.py
) else (
    python launch_desktop_app.py
)
pause
