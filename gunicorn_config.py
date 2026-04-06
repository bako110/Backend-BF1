"""
Gunicorn configuration for BF1 Backend
"""
import os
import multiprocessing

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '8080')}"
backlog = 2048

# Worker processes
# Sur Fly.io (1 vCPU) : 2 workers suffisent, evite la surcharge au demarrage
workers = int(os.getenv("WEB_CONCURRENCY", max(2, multiprocessing.cpu_count())))
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
preload_app = True
timeout = 300       # 5 minutes pour supporter l'upload de videos jusqu'a 70 Mo
graceful_timeout = 30  # Temps pour finir les requetes en cours avant de tuer un worker
keepalive = 5

# Restart workers after this many seconds, to prevent memory leaks
max_worker_memory = 150  # MB
worker_tmp_dir = "/dev/shm"  # Use memory filesystem for better performance

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "bf1-backend"

# Server mechanics
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = "/tmp"

# SSL (handled by Fly.io)
# keyfile = None
# certfile = None

def when_ready(server):
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    worker.log.info("worker received INT or QUIT signal")

def pre_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    worker.log.info("Worker initialized (pid: %s)", worker.pid)

def worker_abort(worker):
    worker.log.info("Worker aborted (pid: %s)", worker.pid)