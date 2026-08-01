"""
Redis Client Manager
Manages connection pool to Redis for caching & JWT blacklisting.
"""

from typing import Optional
import redis.asyncio as aioredis
from config.settings_fastapi import settings

redis_client: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    """
    Returns global async Redis client instance.
    Initializes connection if not yet connected.
    """
    global redis_client
    if redis_client is None:
        redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return redis_client


async def close_redis() -> None:
    """Close Redis connection pool gracefully on app shutdown."""
    global redis_client
    if redis_client is not None:
        await redis_client.close()
        redis_client = None
