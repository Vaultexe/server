import redis.asyncio as aioredis

from app.core.config import settings

async_redis_pool = aioredis.ConnectionPool.from_url(str(settings.REDIS_URI))


class AsyncRedisClient(aioredis.Redis):
    def __init__(self):
        super().__init__(
            connection_pool=async_redis_pool,
            decode_responses=True,
        )
