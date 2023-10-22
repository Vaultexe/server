import datetime as dt
import uuid
from typing import Self

from pydantic import EmailStr, computed_field, model_validator

from app.core.security import hash_pwd
from app.schemas.base import BaseSchema
from app.utils.regex import generate_password


class UserInvite(BaseSchema):
    email: EmailStr
    is_admin: bool = False

    @computed_field(description="Auto generated password on invitation")
    @property
    def master_pwd_hash(self) -> str:
        pwd = generate_password()
        return hash_pwd(pwd)


class UserLogin(BaseSchema):
    email: EmailStr
    master_pwd: str


class UserResetPassword(BaseSchema):
    curr_pwd_hash: str
    new_pwd_hash: str

    @model_validator(mode="after")
    def check_pwds_diff(self) -> Self:
        """Check that new password is different from current password."""
        if self.curr_pwd_hash and self.new_pwd_hash and self.curr_pwd_hash == self.new_pwd_hash:
            raise ValueError("New password must be different from current password")
        return self


class User(BaseSchema):
    id: uuid.UUID
    email: EmailStr
    email_verified: bool
    last_pwd_change: dt.datetime | None
    last_email_change: dt.datetime | None
