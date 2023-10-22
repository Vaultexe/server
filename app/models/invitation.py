import datetime as dt
import uuid
from typing import Self, override

import sqlalchemy.dialects.postgresql as pg
from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app import schemas
from app.models.base import BaseModel


class Invitation(BaseModel):
    """User invitation model"""

    token_hash: Mapped[str] = mapped_column(primary_key=True, nullable=False)
    invitee_id: Mapped[uuid.UUID] = mapped_column(pg.UUID(as_uuid=True), ForeignKey("user.id"), index=True, nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(pg.UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    expires_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_valid: Mapped[bool] = mapped_column(nullable=False, default=True)

    @property
    def is_expired(self) -> bool:
        return self.expires_at > dt.datetime.now(dt.UTC)

    @override
    @classmethod
    def create_from(cls, obj: schemas.InvitationCreate) -> Self:
        return super().create_from(obj)
