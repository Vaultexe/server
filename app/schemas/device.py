import datetime as dt
import uuid

from pydantic import IPvAnyAddress

from app.schemas.base import BaseSchema


class Device(BaseSchema):
    id: uuid.UUID
    user_id: uuid.UUID
    user_agent: str
    regeistered_at: dt.datetime
    last_login_ip: dt.datetime
    last_login_at: dt.datetime


class DeviceCreate(BaseSchema):
    user_id: uuid.UUID
    user_agent: str
    ip: IPvAnyAddress
    is_verified: bool = False
