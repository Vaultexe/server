import datetime as dt
import uuid

from pydantic import ConfigDict

from app.schemas.base import BaseSchema
from app.schemas.enums import CipherType


class CipherBase(BaseSchema):
    pass


class CipherCreate(CipherBase):
    collection_id: uuid.UUID | None = None
    type: CipherType
    data: bytes


class CipherUpdate(CipherBase):
    collection_id: uuid.UUID | None = None
    data: bytes | None = None


class Cipher(CipherBase):
    id: uuid.UUID
    user_id: uuid.UUID
    collection_id: uuid.UUID | None
    type: CipherType
    data: bytes
    created_at: dt.datetime
    updated_at: dt.datetime | None
    deleted_at: dt.datetime | None

    model_config = ConfigDict(from_attributes=True)
