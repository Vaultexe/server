import datetime as dt
import uuid
from typing import Self

import sqlalchemy.dialects.postgresql as pg
from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core import security
from app.models import BaseModel

"""
    Email:
        Max length of email address is 254 characters (We chose max 100), see:
        https://stackoverflow.com/questions/1199190/what-is-the-optimal-length-for-an-email-address-in-a-database
    Password:
        passwords are hashed using agron2 which automatically generates a salt
"""


class User(BaseModel):
    id: Mapped[uuid.UUID] = mapped_column(pg.UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(length=100), nullable=False, unique=True)
    email_verified: Mapped[bool] = mapped_column(nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=False)
    is_admin: Mapped[bool] = mapped_column(nullable=False, default=False)
    master_pwd_hash: Mapped[str] = mapped_column(nullable=False)
    master_pwd_hint: Mapped[str | None] = mapped_column(nullable=True)
    last_pwd_change: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_email_change: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    def update_password(self, password: str) -> Self:
        """Hashes the already 2 time KDF hash of master password client side"""
        self.master_pwd_hash = security.hash_pwd(password)
        return self

    def activate(self) -> Self:
        """Activate user"""
        self.is_active = True
        return self
