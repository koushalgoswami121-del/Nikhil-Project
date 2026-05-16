@echo off
cd /d "%~dp0"
echo Installing dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt -q
echo Starting Coach AI at http://127.0.0.1:8080
".venv\Scripts\python.exe" app.py
pause
