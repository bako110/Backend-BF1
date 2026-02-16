from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio

# ======================
# Rate Limiter performant
# ======================
class RateLimiter:
    def __init__(self, requests_per_minute: int = 100000):
        self.requests_per_minute = requests_per_minute
        self.clients = defaultdict(lambda: {"count": 0, "reset": datetime.utcnow()})
        self.lock = asyncio.Lock()
    
    async def is_allowed(self, identifier: str) -> bool:
        async with self.lock:
            now = datetime.utcnow()
            client = self.clients[identifier]

            # Reset du compteur chaque minute
            if now >= client["reset"]:
                client["count"] = 0
                client["reset"] = now + timedelta(minutes=1)

            if client["count"] >= self.requests_per_minute:
                return False

            client["count"] += 1
            return True

# ======================
# Middleware FastAPI
# ======================
class RateLimitMiddleware(BaseHTTPMiddleware):
    # Endpoints à exclure du rate limit
    EXCLUDED_PATHS = {
        "/openapi.json",
        "/docs",
        "/redoc",
        "/health",
    }

    # Localhost IPs → dev
    LOCALHOST_IPS = {"127.0.0.1", "localhost", "::1"}

    # Production IPs → Render ou serveurs internes
    # Laisse vide pour appliquer le rate limit à toutes les IP externes
    PRODUCTION_IPS = set()

    def __init__(self, app, requests_per_minute: int = 100000):
        super().__init__(app)
        self.limiter = RateLimiter(requests_per_minute)

    async def dispatch(self, request: Request, call_next):
        # Ignore les chemins exclus
        if request.url.path in self.EXCLUDED_PATHS:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"

        # Dev : ignore localhost
        if client_ip in self.LOCALHOST_IPS:
            return await call_next(request)

        # Prod : applique le rate limit pour toutes les IP externes
        if not await self.limiter.is_allowed(client_ip):
            raise HTTPException(
                status_code=429,
                detail=f"Too many requests from {client_ip}. Please try again later."
            )

        response = await call_next(request)
        return response

