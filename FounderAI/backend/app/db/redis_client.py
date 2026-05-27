"""
Redis async client for pub/sub real-time updates.
"""
from __future__ import annotations

import redis.asyncio as aioredis
from ..config import settings

_client: aioredis.Redis | None = None


def get_redis() -> aioredis.Redis:
    global _client
    if _client is None:
        _client = aioredis.from_url(settings.redis_url, decode_responses=True)
    return _client


async def publish(channel: str, message: str) -> None:
    r = get_redis()
    await r.publish(channel, message)


async def close_redis() -> None:
    global _client
    if _client:
        await _client.aclose()
        _client = None
