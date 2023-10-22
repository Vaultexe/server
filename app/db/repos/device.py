import uuid

import sqlalchemy as sa
from pydantic import IPvAnyAddress
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.db.repos.base import BaseRepo


class DeviceRepo(BaseRepo[models.Device, schemas.DeviceCreate]):
    """Device repo"""

    async def clear_redundant_devices(
        self,
        db: AsyncSession,
        *,
        user_id: uuid.UUID,
        ip: IPvAnyAddress | str,
        user_agent: str,
        exclude_id: uuid.UUID = None,
    ) -> int:
        """
        Clears redundant unverified devices
        coming from same ip & user agent

        Returns number of deleted devices
        """
        query = sa.delete(models.Device).where(
            sa.and_(
                models.Device.user_id == user_id,
                models.Device.last_login_ip == ip,
                models.Device.user_agent == user_agent,
                models.Device.is_verified is False,
                models.Device.id != exclude_id,
            )
        )
        result: sa.CursorResult = await db.execute(query)
        return result.rowcount


device = DeviceRepo(models.Device)
