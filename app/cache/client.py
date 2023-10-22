from collections.abc import AsyncGenerator, Mapping
from contextlib import asynccontextmanager
from typing import Any, overload

import redis.asyncio as aioredis
from redis.asyncio.client import Pipeline

from app.core.config import settings
from app.utils.coders import JsonCoder

async_redis_pool = aioredis.ConnectionPool.from_url(str(settings.REDIS_URI))


class AsyncRedisClient:
    """
    Redis client wrapper.
    """

    def __init__(self) -> None:
        self.redis: aioredis.Redis = aioredis.Redis(connection_pool=async_redis_pool)

    @overload
    async def set(self, key: str, value: Any, *, ttl: int) -> bool:
        ...

    @overload
    async def set(self, key: str, value: Any, *, keepttl: bool) -> bool:
        ...

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
        keepttl: bool | None = None,
    ) -> bool:
        """
        Set a key-value pair in Redis.

        Either ttl or keepttl must be specified but not both.

        Overloads:
            set(self, key: str, value: Any, *, ttl: int) -> bool
            set(self, key: str, value: Any, *, keepttl: bool) -> bool

        Args:
            key (str): Key to set.
            value (Any): Value to set.
            ttl (int, optional): Expiration time in seconds. Defaults to None.
            keepttl (bool, optional): Keep the TTL of the key. Defaults to False.

        Returns:
            bool: True if successful, False otherwise.
        """
        value = self.encode(value)

        if ttl is not None and keepttl is not None:
            raise ValueError("Either ttl or keepttl must be specified but not both.")
        elif ttl is not None:
            res = await self.redis.set(key, value, ex=ttl)
        elif keepttl is not None:
            ttl = await self.redis.ttl(key)
            if ttl == -2:
                # key does not exist
                return False
            res = await self.redis.set(key, value, keepttl=keepttl)
        else:
            raise ValueError("Either ttl or keepttl must be specified but not both.")

        return True if res else False

    async def set_many(self, key_value_pairs: Mapping[str, Any], ttl: int) -> bool:
        """
        Set multiple key-value pairs in Redis.

        Returns:
            True if successful, False otherwise.
        """
        async with self.pipeline() as pipe:
            for key, value in key_value_pairs.items():
                value = self.encode(value)
                pipe.set(key, value, ex=ttl)
            return await pipe.execute()

    async def get(self, key: str) -> Any | None:
        """
        Get a value from Redis.

        Returns:
            Value if successful, None otherwise.
        """
        value = await self.redis.get(key)
        return self.decode(value)

    async def get_with_ttl(self, key: str) -> tuple[int, Any | None]:
        """
        Get a value from Redis with its TTL.

        Returns:
            - (ttl, value) if successful
            - (-2, None) if key does not exist
            - (-1, None) if key has no expire set
        """
        async with self.pipeline() as pipe:
            pipe.ttl(key)
            pipe.get(key)
            ttl, value = await pipe.execute()
        return ttl, self.decode(value)

    async def get_all_startswith(
        self,
        key_prefix: str,
    ) -> dict[str, Any]:
        """
        Get all key-value pairs starting with a given prefix.

        Returns:
            Dictionary of key-value pairs.
        """
        keys = await self.redis.keys(f"{key_prefix}*")
        values = await self.redis.mget(keys)
        values = [self.decode(value) for value in values]
        return dict(zip(keys, values, strict=True))

    async def delete(self, key: str) -> bool:
        """
        Delete a key from Redis.

        Returns:
            True if successful, False otherwise.
        """
        return await self.redis.delete(key) == 1

    async def delete_many(self, keys: list[str]) -> int:
        """
        Delete multiple keys from Redis.

        Returns:
            Number of keys deleted.
        """
        return await self.redis.delete(*keys)

    async def delete_all_startswith(self, key_prefix: str) -> int:
        """
        Delete all keys starting with a given prefix.

        Returns:
            Number of keys deleted.
        """
        keys = await self.get_all_startswith(key_prefix)
        return await self.redis.delete(*keys)

    async def flushall(self) -> bool:
        """Delete all cache"""
        return await self.redis.flushall()

    async def exists(self, key: str) -> bool:
        """Check if a key exists in cache"""
        return await self.redis.exists(key) == 1

    async def expire(self, key: str, expire: int) -> bool:
        """
        Set a key's expiration time in Redis.

        Returns:
            True if successful, False otherwise.
        """
        return await self.redis.expire(key, expire)

    async def ttl(self, key: str) -> int:
        """
        Get a key's TTL in Redis.

        Returns:
            - ttl if key exists
            - -2 if key does not exist
            - -1 if key has no expire set
        """
        return await self.redis.ttl(key)

    @asynccontextmanager
    async def pipeline(self, transactional: bool = True) -> AsyncGenerator[Pipeline, None]:
        """
        Create a pipeline for Redis commands.

        Returns:
            Redis pipeline.
        """
        yield self.redis.pipeline(transaction=transactional)

    def encode(self, value: Any) -> bytes:
        return JsonCoder.encode(value)

    def decode(self, value: bytes | None) -> Any:
        if value is None:
            return None
        return JsonCoder.decode(value)
