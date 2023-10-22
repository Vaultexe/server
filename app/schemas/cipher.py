import datetime as dt
import uuid

from app.schemas.base import BaseSchema
from app.schemas.enums import CipherType


class Cipher(BaseSchema):
    id: uuid.UUID
    user_id: uuid.UUID
    collection_id: uuid.UUID | None
    type: CipherType
    data: bytes
    created_at: dt.datetime
    updated_at: dt.datetime | None
    deleted_at: dt.datetime | None


class CipherCreate(BaseSchema):
    user_id: uuid.UUID
    collection_id: uuid.UUID | None
    type: CipherType
    data: bytes


class CipherUpdate(BaseSchema):
    collection_id: uuid.UUID | None
    data: bytes | None
