import datetime as dt
import uuid

from app.schemas.base import BaseSchema


class Device(BaseSchema):
    id: uuid.UUID
    user_id: uuid.UUID
    user_agent: str
    regeistered_at: dt.datetime
    last_login_ip: dt.datetime
    last_login_at: dt.datetime


class DeviceCreate(BaseSchema):
    id: uuid.UUID
    user_id: uuid.UUID
    user_agent: str


def user_agent_extract(ua: str) -> dict:
    """Extracts device id, device type and os from user agent string."""
