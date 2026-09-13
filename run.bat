@echo off
echo ========================================================
echo [run.bat] Launching AegisOR Surgical Safety Guardrail
echo URL: http://127.0.0.1:7860/aegisor
echo ========================================================
cd /d "%~dp0"
uv run python app.py
pause
