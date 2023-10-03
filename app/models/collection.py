import datetime as dt
import uuid

import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy.orm import Mapped, mapped_column

from app.models import BaseModel


class Collection(BaseModel):
    id: Mapped[uuid.UUID] = mapped_column(pg.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(pg.UUID(as_uuid=True), sa.ForeignKey("user.id"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(sa.String, nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())
