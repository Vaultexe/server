import datetime as dt
import uuid

from pydantic import ConfigDict

from app.schemas.base import BaseSchema


class CollectionCreate(BaseSchema):
    name: str


class CollectionUpdate(BaseSchema):
    name: str


class Collection(BaseSchema):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    created_at: dt.datetime

    model_config = ConfigDict(from_attributes=True)
