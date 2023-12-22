import uuid

from app import cache
from app.cache.client import AsyncRedisClient
from app.events.sync_data import SyncData
from app.schemas import Cipher, Collection
from app.schemas.enums import Op


async def notify(
    rc: AsyncRedisClient,
    *,
    user_id: uuid.UUID,
    data: Collection | Cipher,
    action: Op,
) -> None:
    """Notify user vault changes"""
    type = "collection" if isinstance(data, Collection) else "cipher"
    sync_data = SyncData(action=action, data=data, type=type)
    await rc.redis.publish(
        cache.keys.sync_vault_pubsub(user_id),
        sync_data.model_dump_json(),
    )
