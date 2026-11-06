@echo off
REM Schedule in Windows Task Scheduler for weekdays ~8:00 AM Central (the market opens 8:30 AM CT).
cd /d "%~dp0"
set SEC_USER_AGENT=Your Name your@email.com
python -m tradescout score
python -m tradescout picks --account 10000 --risk 1 --open
