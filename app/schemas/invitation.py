import datetime as dt
import uuid

from pydantic import ConfigDict, Field, computed_field

from app.core import security
from app.schemas.base import BaseSchema


class InvitationCreate(BaseSchema):
    token: uuid.UUID = Field(exclude=True)
    invitee_id: uuid.UUID
    created_by: uuid.UUID
    created_at: dt.datetime | None = None
    expires_at: dt.datetime | None = None

    @computed_field
    def token_hash(self) -> str:
        return security.sha256_hash(self.token.hex.encode())


class Invitation(BaseSchema):
    token_hash: str
    invitee_id: uuid.UUID
    created_by: uuid.UUID
    created_at: dt.datetime
    expires_at: dt.datetime
    is_valid: bool

    model_config = ConfigDict(from_attributes=True)
