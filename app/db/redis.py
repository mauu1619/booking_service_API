from collections.abc import AsyncGenerator

import redis.asyncio as redis
from redis.asyncio import Redis

from app.core.config import settings


async def get_redis_session() -> AsyncGenerator[Redis, None]:

    async with redis.from_url(settings.redis_url, decode_responses=True) as session:
        yield session
