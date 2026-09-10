@echo off
cd /d "%~dp0"

if not exist ".venv" (
    echo Premier lancement : preparation de l'environnement...
    echo Installation des dépendances...
    python -m venv .venv
    .venv\Scripts\python.exe -m pip install --upgrade pip
    .venv\Scripts\python.exe -m pip install -r requirements.txt
)

.venv\Scripts\python.exe -m caquot.main
pause
