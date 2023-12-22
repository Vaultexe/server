"""
    This module is used to check the connection to the database.
    It is called from the Dockerfile as part of the entrypoint.
"""

import asyncio
import logging

from async_timeout import timeout
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.cache.client import AsyncRedisClient
from app.db.session import AsyncSessionFactory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


TIMEOUT = 5  # seconds
MAX_TRIES = 5
WAIT_TIME = 1  # seconds


@retry(
    stop=stop_after_attempt(MAX_TRIES),
    wait=wait_fixed(WAIT_TIME),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def init_db_connection() -> None:
    """Wait till database connection is established"""
    try:
        async with timeout(TIMEOUT):
            async with AsyncSessionFactory() as session:
                session: AsyncSession
                await session.execute(text("SELECT 1"))
    except Exception as e:
        logger.error("--- Connection to DB failed ---")
        logger.log(logging.ERROR, e)
        raise e


@retry(
    stop=stop_after_attempt(MAX_TRIES),
    wait=wait_fixed(WAIT_TIME),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def init_redis_connection() -> None:
    """Wait till redis connection is established"""
    try:
        async with timeout(TIMEOUT):
            redis = AsyncRedisClient()
            await redis.ping()
    except Exception as e:
        logger.error("--- Connection to Redis failed ---")
        logger.log(logging.ERROR, e)
        raise e


async def main() -> None:
    logger.info("--- Connecting TO POSTGRESQL DB ---")
    await init_db_connection()
    logger.info("--- Connection TO POSTGRESQL DB ESTABLISHED ---")

    logger.info("--- Connecting TO REDIS ---")
    await init_redis_connection()
    logger.info("--- Connection TO REDIS ESTABLISHED ---")


if __name__ == "__main__":
    asyncio.run(main())
