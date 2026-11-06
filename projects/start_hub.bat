@echo off
REM One-click launcher for all apps. First run installs dependencies.
cd /d "%~dp0"
if not exist ".deps_installed" (
  echo Installing dependencies (first run only)...
  python -m pip install -r requirements-all.txt && echo ok > .deps_installed
)
cd hub
python -m hub
