import datetime as dt
import uuid

from app.schemas.base import BaseSchema


class Collection(BaseSchema):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    created_at: dt.datetime


class CollectionCreate(BaseSchema):
    user_id: uuid.UUID
    name: str
