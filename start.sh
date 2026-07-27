#!/bin/bash
cd "$(dirname "$0")"

PORT=${PORT:-8080}
WORKERS=${WEB_CONCURRENCY:-2}
VENV_UVICORN="venv/bin/uvicorn"

echo "Mise à jour du projet..."
git pull origin main

if [ ! -x "$VENV_UVICORN" ]; then
    echo "Erreur: $VENV_UVICORN introuvable. Créez le venv et installez requirements.txt."
    exit 1
fi

echo "Arrêt de l'ancien serveur..."
pkill -f "uvicorn app.main:app" 2>/dev/null
sleep 1

echo "Démarrage du serveur..."
nohup "$VENV_UVICORN" app.main:app \
    --host 0.0.0.0 \
    --port $PORT \
    --workers $WORKERS \
    --log-level info \
    > uvicorn.log 2>&1 &

echo "Backend démarré sur le port $PORT (PID $!)"
