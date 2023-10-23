import datetime as dt
import uuid
from typing import override

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy.orm import Mapped, mapped_column

from app import schemas
from app.models import BaseModel
from app.models.enums import PgCipherType
from app.schemas.enums import CipherType


class Cipher(BaseModel):
    id: Mapped[uuid.UUID] = mapped_column(pg.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(pg.UUID(as_uuid=True), sa.ForeignKey("user.id"), index=True, nullable=False)
    collection_id: Mapped[uuid.UUID | None] = mapped_column(
        pg.UUID(as_uuid=True), sa.ForeignKey("collection.id"), index=True, nullable=True
    )
    type: Mapped[CipherType] = mapped_column(PgCipherType, nullable=False)
    data: Mapped[bytes] = mapped_column(sa.LargeBinary(), nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
    updated_at: Mapped[dt.datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True, onupdate=sa.func.now())
    deleted_at: Mapped[dt.datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)

    @override
    def import_from(self, obj: schemas.CipherBase) -> None:
        return super().import_from(obj, exclude_unset=True)

    def soft_delete(self) -> None:
        self.deleted_at = dt.datetime.now(dt.UTC)
