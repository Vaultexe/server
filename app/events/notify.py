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
    data: Collection | Cipher | uuid.UUID,
    action: Op,
) -> None:
    """Notify user vault changes"""
    sync_data = SyncData(action=action, data=data, type=get_type(data))
    await rc.publish(
        cache.keys.sync_vault_pubsub(user_id),
        sync_data.model_dump_json(),
    )

def get_type(data):
    if isinstance(data, Collection):
        return "collection"
    elif isinstance(data, Cipher):
        return "cipher"
    else:
        return "id"
