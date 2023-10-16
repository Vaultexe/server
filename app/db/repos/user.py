import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
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


user = UserRepo(models.User)
