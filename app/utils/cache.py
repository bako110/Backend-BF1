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
        self.enabled = os.getenv("REDIS_ENABLED", "false").lower() == "true"
        
    async def connect(self):
        if not self.enabled or not REDIS_AVAILABLE:
            return
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            await self.redis_client.ping()
        except Exception as e:
            print(f"Redis connection failed: {e}. Caching disabled.")
            self.redis_client = None
    
    async def disconnect(self):
        if self.redis_client:
            await self.redis_client.close()
    
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
        if not self.redis_client:
            return
        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                await self.redis_client.delete(*keys)
        except Exception:
            pass

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
