import datetime as dt
import uuid

from pydantic import ConfigDict, IPvAnyAddress

from app.schemas.base import BaseSchema


class DeviceCreate(BaseSchema):
    user_id: uuid.UUID
    user_agent: str
    ip: IPvAnyAddress
    is_verified: bool = False


class Device(BaseSchema):
    id: uuid.UUID
    user_id: uuid.UUID
    user_agent: str
    regeistered_at: dt.datetime
    last_login_ip: dt.datetime
    last_login_at: dt.datetime

    model_config = ConfigDict(from_attributes=True)
