#!/bin/bash
PORT=${PORT:-8080}
WORKERS=${WEB_CONCURRENCY:-2}

pkill -f "uvicorn app.main:app" 2>/dev/null
sleep 1

nohup uvicorn app.main:app \
    --host 0.0.0.0 \
    --port $PORT \
    --workers $WORKERS \
    --log-level info \
    > uvicorn.log 2>&1 &

echo "BF1 Backend démarré sur :$PORT (PID $!)"
