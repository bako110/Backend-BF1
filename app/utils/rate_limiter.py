from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio

class RateLimiter:
    def __init__(self, requests_per_minute: int = 5000):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
        self.lock = asyncio.Lock()
    
    async def is_allowed(self, identifier: str) -> bool:
        async with self.lock:
            now = datetime.utcnow()
            cutoff = now - timedelta(minutes=1)
            
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if req_time > cutoff
            ]
            
            if len(self.requests[identifier]) >= self.requests_per_minute:
                return False
            
            self.requests[identifier].append(now)
            return True

class RateLimitMiddleware(BaseHTTPMiddleware):
    # Endpoints to exclude from rate limiting
    EXCLUDED_PATHS = {
        "/openapi.json",
        "/docs",
        "/redoc",
        "/health",
    }
    # Localhost IPs are not rate limited during development
    LOCALHOST_IPS = {"127.0.0.1", "localhost", "::1", "10.10.0.8", "192.168.11.137"}
    
    def __init__(self, app, requests_per_minute: int = 5000):
        super().__init__(app)
        self.limiter = RateLimiter(requests_per_minute)
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for excluded paths
        if request.url.path in self.EXCLUDED_PATHS:
            return await call_next(request)
        
        client_ip = request.client.host if request.client else "unknown"
        
        # Skip rate limiting for localhost during development
        if client_ip in self.LOCALHOST_IPS:
            return await call_next(request)
        
        if not await self.limiter.is_allowed(client_ip):
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again later."
            )
        
        response = await call_next(request)
        return response
