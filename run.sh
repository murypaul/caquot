#!/usr/bin/env bash
# Lanceur pour Linux/macOS : double-clic ou "./run.sh" dans un terminal.
#
# Au premier lancement, crée un environnement Python isolé (dossier .venv) et y
# installe les dépendances nécessaires (cf. requirements.txt). Les lancements
# suivants réutilisent cet environnement sans tout réinstaller.

set -e
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
    echo "Premier lancement : préparation de l'environnement, merci de patienter..."
    echo "Installation des dépendances..."
    python3 -m venv .venv
    .venv/bin/pip install --quiet --upgrade pip
    .venv/bin/pip install -r requirements.txt
    pip install -e .
fi

.venv/bin/python -m caquot.main
