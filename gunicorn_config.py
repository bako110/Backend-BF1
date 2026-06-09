"""
Gunicorn configuration — VPS production
"""
import os
import multiprocessing

# ── Socket ────────────────────────────────────────────────────────────────────
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
backlog = 2048

# ── Workers ───────────────────────────────────────────────────────────────────
# Règle standard : (2 × CPU) + 1 pour workload I/O-bound (MongoDB, Redis, HTTP)
_cpu = multiprocessing.cpu_count()
workers = int(os.getenv("WEB_CONCURRENCY", (_cpu * 2) + 1))
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000

# Redémarre un worker après N requêtes pour éviter les fuites mémoire
max_requests = 1000
max_requests_jitter = 100

# Charge l'app une seule fois dans le master et la partage (évite init×workers)
preload_app = True

# ── Timeouts ──────────────────────────────────────────────────────────────────
timeout = 120           # 2 min max par requête (uploads inclus)
graceful_timeout = 30   # Temps accordé aux workers pour finir avant kill
keepalive = 5           # Secondes de keep-alive HTTP

# ── Répertoires temporaires ───────────────────────────────────────────────────
# /dev/shm = RAM filesystem, plus rapide que /tmp pour les heartbeats Gunicorn
worker_tmp_dir = "/dev/shm" if os.path.exists("/dev/shm") else "/tmp"
tmp_upload_dir = "/tmp"

# ── Logging ───────────────────────────────────────────────────────────────────
accesslog = "-"
errorlog  = "-"
loglevel  = os.getenv("LOG_LEVEL", "info")
access_log_format = '%(h)s "%(r)s" %(s)s %(b)sB %(D)sμs'

# ── Process ───────────────────────────────────────────────────────────────────
proc_name = "bf1-backend"
daemon    = False

# ── Hooks ─────────────────────────────────────────────────────────────────────
def when_ready(server):
    server.log.info(f"BF1 Backend prêt — {workers} workers sur :{os.getenv('PORT', '8000')}")

def on_exit(server):
    server.log.info("BF1 Backend arrêté proprement")

def worker_abort(worker):
    worker.log.warning(f"Worker {worker.pid} abandonné")