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

    async def restore(
        self,
        db: AsyncSession,
        *,
        id: uuid.UUID,
    ) -> models.Cipher | None:
        """
        Restore a soft deleted cipher
        Return cipher if exists else returns None
        """
        query = (
            sa.update(self.model)
            .where(self.model.id == id)
            .values(deleted_at=None)
            .returning(self.model)
        )
        result = await db.scalar(query)
        return result

    async def permanent_delete(
        self,
        db: AsyncSession,
        *,
        id: uuid.UUID,
    ) -> bool:
        """
        Permanent delete cipher
        Return True if cipher is deleted else False if cipher does not exist
        """
        query = sa.delete(self.model).where(self.model.id == id)
        result = await db.execute(query)
        return bool(result.rowcount)

    async def soft_delete_collection(
        self,
        db: AsyncSession,
        *,
        id: uuid.UUID,
    ) -> list[uuid.UUID]:
        """
        Soft delete all ciphers in a collection
        Returns list of cipher ids
        """
        query = (
            sa.update(self.model)
            .where(self.model.collection_id == id)
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
        filters = sa.and_(self.model.user_id == user_id, self.model.deleted_at == None)
        return await super()._get_all(db, filter=filters)

    @deprecated("Use it in development only", category=DeprecationWarning)
    async def _get_all_deleted(
        self,
        db: AsyncSession,
        *,
        user_id: uuid.UUID,
    ) -> list[models.Cipher]:
        filters = sa.and_(self.model.user_id == user_id, self.model.deleted_at != None)
        return await super()._get_all(db, filter=filters)

cipher = CipherRepo(models.Cipher)
