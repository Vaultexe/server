import uuid
from collections.abc import AsyncIterator

from app import cache
from app.cache.client import AsyncRedisClient

__pubsub_settings__ = {
    "ignore_subscribe_messages": True,
}


async def listen(
    rc: AsyncRedisClient,
    *,
    user_id: uuid.UUID,
) -> AsyncIterator:
    """Listen for user vault changes"""
    async with rc.pubsub(**__pubsub_settings__) as pubsub:
        await pubsub.subscribe(cache.keys.sync_vault_pubsub(user_id))
        async for message in pubsub.listen():
            if message["type"] == "message":
                yield message["data"]
