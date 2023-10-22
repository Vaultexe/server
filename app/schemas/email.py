import datetime as dt

from pydantic import EmailStr

from app.schemas.base import BaseSchema


class EmailPayload(BaseSchema):
    to: EmailStr
    subject: str
    ccs: EmailStr | list[EmailStr] | None = None


class RegistrationEmailPayload(EmailPayload):
    subject: str = "Register into Vaultexe"
    token: str
    expires_in_hours: int


class OTPEmailPayload(EmailPayload):
    subject: str = "New Vaultexe OTP"
    otp: str
    expires_at: dt.datetime
