import uuid
from collections.abc import AsyncIterator

from app.cache.client import AsyncRedisClient
from app.cache.key_gen import KeyGen

__pubsub_settings__ = {
    "ignore_subscribe_messages": True,
}

async def listen(
    rc: AsyncRedisClient,
    *,
    user_id: uuid.UUID,
) -> AsyncIterator:
    """Listen for user vault changes"""
    async with rc.redis.pubsub(**__pubsub_settings__) as pubsub:
        await pubsub.subscribe(KeyGen.USER_SYNC_VAULT_PUBSUB_CHANNEL(user_id))
        async for message in pubsub.listen():
            if message["type"] == "message":
                yield message["data"]
