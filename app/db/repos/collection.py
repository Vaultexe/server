import uuid
from typing import override

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import deprecated

from app import models, schemas
from app.db.repos.base import BaseRepo


class CollectionRepo(BaseRepo[models.Collection, schemas.CollectionCreate]):
    """Cipher repo"""

    @override
    async def create(
        self,
        db: AsyncSession,
        *,
        user_id: uuid.UUID,
        obj_in: schemas.CollectionCreate,
    ) -> models.Collection:
        collection = await super().create(db, obj_in=obj_in)
        collection.user_id = user_id
        return collection

    async def delete(self, db: AsyncSession, *, id: uuid.UUID) -> bool:
        query = sa.delete(self.model).where(self.model.id == id).returning(self.model.id)
        result = await db.scalar(query)
        return result is not None

    @deprecated("Use it in development only", category=DeprecationWarning)
    @override
    async def _get_all(
        self,
        db: AsyncSession,
        *,
        user_id: uuid.UUID,
    ) -> list[models.Collection]:
        filters = self.model.user_id == user_id
        return await super()._get_all(db, filter=filters)


collection = CollectionRepo(models.Collection)
