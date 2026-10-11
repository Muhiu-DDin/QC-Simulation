@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Install Python dependencies as described in README.md first.
  pause
  exit /b 2
)
".venv\Scripts\python.exe" tools\prepare_vercel.py
if errorlevel 1 (
  echo Website preparation failed. Review the message above.
  pause
  exit /b 1
)
start "" "http://127.0.0.1:8000/calculator.html"
".venv\Scripts\python.exe" serve.py
pause
