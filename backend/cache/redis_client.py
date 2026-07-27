import redis.asyncio as redis
from typing import AsyncGenerator
from backend.config.settings import settings

# Global redis pool
redis_pool = redis.ConnectionPool.from_url(
    settings.redis_url, 
    decode_responses=True
)

async def get_redis() -> AsyncGenerator[redis.Redis, None]:
    """Dependency to get redis connection"""
    client = redis.Redis(connection_pool=redis_pool)
    try:
        yield client
    finally:
        await client.close()
