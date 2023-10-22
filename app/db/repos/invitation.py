import uuid

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.core import security


class InvitationRepo:
    """Invitation repository."""

    async def get_by_token(
        self,
        db: AsyncSession,
        *,
        token: str,
    ) -> models.Invitation | None:
        """Get invitation by token."""
        token_hash = security.sha256_hash(token.encode())
        query = sa.select(models.Invitation).where(models.Invitation.token_hash == token_hash)
        return await db.scalar(query)

    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: schemas.InvitationCreate,
    ) -> models.Invitation:
        """Create new invitation"""
        db_obj = models.Invitation.create_from(obj_in)
        db.add(db_obj)
        return db_obj

    async def invalidate_tokens(
        self,
        db: AsyncSession,
        *,
        user_id: uuid.UUID,
    ) -> int:
        """
        Invalidate all user invitation tokens.

        Returns:
            Number of invalidated invitations
        """
        query = (
            sa.update(models.Invitation)
            .where(models.Invitation.invitee_id == user_id)
            .where(models.Invitation.is_valid)
            .values(is_valid=False)
        )
        res: sa.ResultProxy = await db.execute(query)  # type: ignore
        return res.rowcount


invitation = InvitationRepo()
