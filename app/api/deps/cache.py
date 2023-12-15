from typing import Annotated

import redis
import rq
from fastapi import Depends

from app.cache.client import AsyncRedisClient
from app.core.config import settings
from app.schemas.enums import WorkerQueue

sync_redis_pool = redis.ConnectionPool.from_url(str(settings.REDIS_URI))

def get_sync_redis_conn() -> redis.Redis:
    return redis.Redis(connection_pool=sync_redis_pool)


def get_mq_low() -> rq.Queue:
    return rq.Queue(WorkerQueue.LOW, connection=get_sync_redis_conn())


def get_mq_default() -> rq.Queue:
    return rq.Queue(WorkerQueue.DEFAULT, connection=get_sync_redis_conn())


def get_mq_high() -> rq.Queue:
    return rq.Queue(WorkerQueue.HIGH, connection=get_sync_redis_conn())


""" Annotated Dependency """
AsyncRedisClientDep = Annotated[AsyncRedisClient, Depends()]
SyncRedisClientDep = Annotated[redis.Redis, Depends(get_sync_redis_conn)]

MQLow = Annotated[rq.Queue, Depends(get_mq_low)]
MQDefault = Annotated[rq.Queue, Depends(get_mq_default)]
MQHigh = Annotated[rq.Queue, Depends(get_mq_high)]
