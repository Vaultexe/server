import datetime as dt
import uuid

import sqlalchemy.dialects.postgresql as pg
from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import IPvAnyAddress
from app.models import BaseModel
from sqlalchemy import ForeignKey


''' 
max length of ipv6/ipv4 address is 45 characters, see:
https://stackoverflow.com/questions/166132/maximum-length-of-the-textual-representation-of-an-ipv6-address/166157#166157

'''

class Device(BaseModel):
    id: Mapped[uuid.UUID] = mapped_column(pg.UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(pg.UUID(as_uuid=True), ForeignKey("user.id"), index=True, nullable=False)
    device_type: Mapped[str] = mapped_column(nullable=False)
    device_os: Mapped[str] = mapped_column(nullable=False)
    regestered_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    last_login_ip: Mapped[IPvAnyAddress] = mapped_column(String(length=45), nullable=False)
    last_login_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    
