import sqlalchemy as sa
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
