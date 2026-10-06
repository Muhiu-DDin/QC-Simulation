@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Create the virtual environment and install requirements as described in README.md.
  pause
  exit /b 2
)
".venv\Scripts\python.exe" run.py --strict
if errorlevel 1 (
  echo Review the reported error or comparison differences.
  pause
  exit /b 1
)
start "" "output\report.html"
pause
