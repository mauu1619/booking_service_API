import redis.asyncio as redis

from app.core.config import settings

async def get_redis_session():
    async with redis.from_url(settings.redis_url, decode_responses=True) as session:
        yield session