import datetime as dt
import uuid

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy.orm import Mapped, mapped_column

from app.models import BaseModel
from app.models.enums import PgCipherType
from app.schemas.enums import CipherType


class Cipher(BaseModel):
    id: Mapped[uuid.UUID] = mapped_column(pg.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(pg.UUID(as_uuid=True), sa.ForeignKey("user.id"), index=True, nullable=False)
    collection_id: Mapped[uuid.UUID] = mapped_column(pg.UUID(as_uuid=True), sa.ForeignKey("collection.id"), index=True, nullable=False)
    type: Mapped[CipherType] = mapped_column(PgCipherType, nullable=False)
    data: Mapped[str] = mapped_column(sa.String, nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    updated_at: Mapped[dt.datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True, server_onupdate=sa.func.now())
