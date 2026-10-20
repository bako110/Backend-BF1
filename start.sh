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

mongo_up() {
    (echo > /dev/tcp/127.0.0.1/27017) >/dev/null 2>&1
}

if ! mongo_up; then
    echo "MongoDB arrêté, démarrage via supervisord..."
    if pgrep -x supervisord >/dev/null; then
        sudo supervisorctl start mongodb
    else
        sudo /usr/bin/supervisord -c /etc/supervisor/supervisord.conf
    fi
    for i in $(seq 1 30); do
        mongo_up && break
        sleep 1
    done
    if ! mongo_up; then
        echo "Erreur: MongoDB n'a pas démarré (voir /var/log/mongodb/mongod.log)."
        exit 1
    fi
    echo "MongoDB démarré."
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
