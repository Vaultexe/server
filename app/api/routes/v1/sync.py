import uuid
from collections.abc import AsyncIterator

from fastapi import APIRouter
from sse_starlette import EventSourceResponse, ServerSentEvent

from app.api.deps import AsyncRedisClientDep, UserDep
from app.cache.client import AsyncRedisClient
from app.cache.key_gen import KeyGen
from app.events import SyncData, listen

router = APIRouter()


@router.get("/", response_model=SyncData)
async def sse(
    user: UserDep,
    rc: AsyncRedisClientDep,
) -> EventSourceResponse:
    """Server sent events for vault syncing"""
    return EventSourceResponse(listen(rc, user_id=user.id))


async def listen_to_updates(
    user_id: uuid.UUID | str,
    rc: AsyncRedisClient,
) -> AsyncIterator:
    async with rc.redis.pubsub() as pubsub:
        await pubsub.subscribe(KeyGen.USER_SYNC_VAULT_PUBSUB_CHANNEL(user_id))
        async for message in pubsub.listen():
            if message["type"] == "message":
                yield ServerSentEvent(SyncData.model_validate_json(message["data"]).model_dump())
