import uuid
from typing import override

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import deprecated

from app import models, schemas
from app.db.repos.base import BaseRepo


class CipherRepo(BaseRepo[models.Cipher, schemas.CipherCreate]):
    """Cipher repo"""

    @override
    async def create(
        self,
        db: AsyncSession,
        *,
        user_id: uuid.UUID,
        obj_in: schemas.CipherCreate,
    ) -> models.Cipher:
        cipher = await super().create(db, obj_in=obj_in)
        cipher.user_id = user_id
        return cipher

    async def soft_delete(
        self,
        db: AsyncSession,
        *,
        id: uuid.UUID,
    ) -> models.Cipher | None:
        """
        Soft delete cipher by marking deleted_at field.
        Return cipher if exists else returns None
        """
        cipher = await self.get(db, id=id)
        if not cipher:
            return None
        cipher.soft_delete()
        return cipher

    async def soft_delete_collection(
        self,
        db: AsyncSession,
        *,
        collection_id: uuid.UUID,
    ) -> list[uuid.UUID]:
        """
        Soft delete all ciphers ina  collection
        Returns list of cipher ids
        """
        query = (
            sa.update(self.model)
            .where(self.model.collection_id == collection_id)
            .values(
                deleted_at=sa.func.now(),
                collection_id=None,
            )
            .returning(self.model.id)
        )
        result = await db.scalars(query)
        return list(result.all())

    @deprecated("Use it in development only", category=DeprecationWarning)
    @override
    async def _get_all(
        self,
        db: AsyncSession,
        *,
        user_id: uuid.UUID,
    ) -> list[models.Cipher]:
        filters = sa.and_(self.model.user_id == user_id, self.model.deleted_at is None)  # type: ignore
        return await super()._get_all(db, filter=filters)


cipher = CipherRepo(models.Cipher)
