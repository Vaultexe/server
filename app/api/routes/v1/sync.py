from fastapi import APIRouter
from sse_starlette import EventSourceResponse

from app.api.deps import AsyncRedisClientDep, UserDep
from app.events import SyncData, listen

router = APIRouter()


@router.get("/", response_model=SyncData)
async def sse(
    user: UserDep,
    rc: AsyncRedisClientDep,
) -> EventSourceResponse:
    """Server sent events for vault syncing"""
    return EventSourceResponse(listen(rc, user_id=user.id))
