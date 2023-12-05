import uuid

from app.cache.client import AsyncRedisClient
from app.cache.key_gen import KeyGen
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
        KeyGen.USER_SYNC_VAULT_PUBSUB_CHANNEL(user_id),
        sync_data.model_dump_json(),
    )

