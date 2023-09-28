import datetime as dt
import uuid

from app.schemas.base import BaseSchema


class Device(BaseSchema):
    id: uuid.UUID
    user_id: uuid.UUID
    device_type: str
    device_os: str
    regeistered_at: dt.datetime
    last_login_ip: dt.datetime
    last_login_at: dt.datetime
