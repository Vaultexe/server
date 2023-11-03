import datetime as dt
import uuid
from typing import Self, override

import sqlalchemy.dialects.postgresql as pg
from pydantic import IPvAnyAddress
from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app import schemas
from app.models import BaseModel
from app.utils.regex import uuid4_str

"""
max length of ipv6/ipv4 address is 45 characters, see:
https://stackoverflow.com/questions/166132/maximum-length-of-the-textual-representation-of-an-ipv6-address/166157#166157

"""


class Device(BaseModel):
    # fmt: off
    id: Mapped[str] = mapped_column(primary_key=True, index=True, default=uuid4_str)
    user_id: Mapped[uuid.UUID] = mapped_column(pg.UUID(as_uuid=True), ForeignKey("user.id"), index=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(nullable=False, default=False)
    user_agent: Mapped[str] = mapped_column(String(length=350), nullable=False)
    regestered_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    last_login_ip: Mapped[IPvAnyAddress] = mapped_column(String(length=45), nullable=False)
    last_login_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    # fmt: on

    def refresh_last_login(self, ip: IPvAnyAddress) -> Self:
        self.last_login_ip = str(ip)
        self.last_login_at = dt.datetime.now(dt.UTC)
        return self

    def verify(self) -> Self:
        self.is_verified = True
        return self

    @override
    def import_from(self, obj: schemas.DeviceCreate) -> Self:
        self.refresh_last_login(obj.ip)
        del obj.ip
        return super().import_from(obj)
