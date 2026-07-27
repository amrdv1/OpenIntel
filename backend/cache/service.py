import json
from typing import Any, Optional
import redis.asyncio as redis

class CacheService:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        # Default TTL is 24 hours (86400 seconds)
        self.default_ttl = 86400

    async def get(self, key: str) -> Optional[Any]:
        data = await self.redis.get(key)
        if data:
            return json.loads(data)
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        if ttl is None:
            ttl = self.default_ttl
        await self.redis.setex(key, ttl, json.dumps(value))

    async def delete(self, key: str) -> None:
        await self.redis.delete(key)
