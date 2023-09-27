import datetime as dt
import uuid

from pydantic import EmailStr

from app.schemas.base import BaseSchema


class UserCreate(BaseSchema):
    name: str
    email: EmailStr
    master_pwd_hash: str
    master_pwd_hint: str | None = None


class UserLogin(BaseSchema):
    email: EmailStr
    master_pwd: str


class User(BaseSchema):
    id: uuid.UUID
    name: str
    email: EmailStr
    email_verified: bool
    last_pwd_change: dt.datetime | None
    last_email_change: dt.datetime | None
