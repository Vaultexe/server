import uuid

import sqlalchemy as sa
from pydantic import IPvAnyAddress
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.db.repos.base import BaseRepo


class DeviceRepo(BaseRepo[models.Device, schemas.DeviceCreate]):
    """Device repo"""

    async def verify(
        self,
        db: AsyncSession,
        *,
        id: str,
    ) -> bool:
        """Verify device"""
        query = sa.update(models.Device).where(models.Device.id == id).values(is_verified=True)
        result: sa.CursorResult = await db.execute(query)
        return bool(result.rowcount)

    async def is_verified(
        self,
        db: AsyncSession,
        *,
        id: str | None,
    ) -> bool:
        """Check if device is verified"""
        if not id:
            return False
        query = sa.select(models.Device.is_verified).where(models.Device.id == id)
        result: sa.Result = await db.execute(query)
        return bool(result.scalar_one())

    async def clear_redundant_devices(
        self,
        db: AsyncSession,
        *,
        user_id: uuid.UUID,
        ip: IPvAnyAddress,
        user_agent: str,
        exclude_id: str | None = None,
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
                models.Device.is_verified is False,  # type: ignore
                models.Device.id != exclude_id,
            )
        )
        result: sa.CursorResult = await db.execute(query)
        return result.rowcount


device = DeviceRepo(models.Device)
