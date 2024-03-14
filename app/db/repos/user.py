from typing import override

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.core import security
from app.db.repos.base import BaseRepo


class UserRepo(BaseRepo[models.User, schemas.UserInvite]):
    """User repo"""

    async def get_by_email(
        self,
        db: AsyncSession,
        email: str,
    ) -> models.User | None:
        """Get user by email or none if not found"""
        query = sa.select(models.User).where(models.User.email == email)
        return await db.scalar(query)

    @override
    async def bulk_create(
        self,
        db: AsyncSession,
        *,
        objs_in: list[schemas.UserInvite]
    ) -> list[models.User]:
        """Create bulk users. Skip conflicts"""
        query = (
            pg.insert(models.User)
            .values([o.model_dump() for o in objs_in])
            .on_conflict_do_nothing(index_elements=[models.User.email])
            .returning(models.User)
        )
        res = await db.scalars(query)
        return list(res.all())

    async def authenticate(
        self,
        db: AsyncSession,
        *,
        email: str,
        password: str,
    ) -> models.User | None:
        """Authenticate user by email and password"""
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not security.verify_pwd(password, user.master_pwd_hash):
            return None
        return user


user = UserRepo(models.User)
