from typing import Annotated

import redis
from fastapi import Depends

from app.cache.client import AsyncRedisClient
from app.core.config import settings


def get_sync_redis_conn() -> redis.Redis:
    return redis.Redis.from_url(str(settings.REDIS_URI))


""" Annotated Dependency """
AsyncRedisClientDep = Annotated[AsyncRedisClient, Depends()]
SyncRedisClientDep = Annotated[redis.Redis, Depends(get_sync_redis_conn)]
