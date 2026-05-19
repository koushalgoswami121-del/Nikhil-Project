@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    py -3.12 -m venv .venv 2>nul || python -m venv .venv
)
echo Installing dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt -q
echo.
echo Starting Coach AI at http://127.0.0.1:8080
echo Do NOT use plain "python app.py" — use this window or start.bat
echo.
".venv\Scripts\python.exe" app.py
pause
