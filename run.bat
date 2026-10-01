@echo off
cd /d "%~dp0"

if not exist ".venv" (
    echo Premier lancement : preparation de l'environnement...
    echo Installation des dependances...
    python -m venv .venv
    .venv\Scripts\python.exe -m pip install --upgrade pip
    .venv\Scripts\python.exe -m pip install -r requirements.txt
    pip install -e .
)

.venv\Scripts\python.exe -m caquot.main
pause
