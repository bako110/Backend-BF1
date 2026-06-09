import json
from typing import Optional, Any
from functools import wraps
import hashlib

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

import os

class CacheManager:
    def __init__(self):
        self.redis_client = None
        self.enabled = os.getenv("REDIS_ENABLED", "true").lower() == "true"

    async def connect(self):
        if not self.enabled or not REDIS_AVAILABLE:
            return
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            self.redis_client = redis.from_url(
                redis_url,
                decode_responses=True,
                max_connections=20,
                socket_connect_timeout=2,
                socket_timeout=2,
                retry_on_timeout=True,
            )
            await self.redis_client.ping()
            print("✅ Redis connecté")
        except Exception as e:
            print(f"⚠️ Redis non disponible: {e}. Cache désactivé.")
            self.redis_client = None

    async def disconnect(self):
        if self.redis_client:
            await self.redis_client.aclose()

    async def get(self, key: str) -> Optional[Any]:
        if not self.redis_client:
            return None
        try:
            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
        except Exception:
            pass
        return None

    async def set(self, key: str, value: Any, ttl: int = 300):
        if not self.redis_client:
            return
        try:
            await self.redis_client.setex(key, ttl, json.dumps(value, default=str))
        except Exception:
            pass

    async def delete(self, key: str):
        if not self.redis_client:
            return
        try:
            await self.redis_client.delete(key)
        except Exception:
            pass

    async def delete_pattern(self, pattern: str):
        """Supprime les clés correspondant au pattern via SCAN (non-bloquant)."""
        if not self.redis_client:
            return
        try:
            cursor = 0
            while True:
                cursor, keys = await self.redis_client.scan(cursor, match=pattern, count=100)
                if keys:
                    await self.redis_client.delete(*keys)
                if cursor == 0:
                    break
        except Exception:
            pass

    async def increment(self, key: str, ttl: int = 86400) -> int:
        """Incrémente un compteur, utile pour rate limiting et stats."""
        if not self.redis_client:
            return 0
        try:
            val = await self.redis_client.incr(key)
            if val == 1:
                await self.redis_client.expire(key, ttl)
            return val
        except Exception:
            return 0

    @property
    def is_connected(self) -> bool:
        return self.redis_client is not None

cache_manager = CacheManager()

def cache_key(*args, **kwargs) -> str:
    key_data = f"{args}{kwargs}"
    return hashlib.md5(key_data.encode()).hexdigest()

def cached(ttl: int = 300, prefix: str = ""):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = f"{prefix}:{cache_key(*args, **kwargs)}"
            cached_value = await cache_manager.get(key)
            if cached_value is not None:
                return cached_value
            result = await func(*args, **kwargs)
            await cache_manager.set(key, result, ttl)
            return result
        return wrapper
    return decorator
