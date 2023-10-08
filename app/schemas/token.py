import datetime as dt
import uuid

from pydantic import Field, IPvAnyAddress

from app.schemas import BaseSchema
from app.schemas.enums import TokenType

"""
JWT: JWT Token Schema

JWT:
    jti: JWT ID
    iat: Issued At
    exp: Expires At
    sub: Subject
    ip: IP Address
"""


class TokenBase(BaseSchema):
    type: TokenType
    jti: uuid.UUID
    iat: dt.datetime
    exp: dt.datetime
    sub: uuid.UUID | str
    is_admin: bool | None = Field(None, exclude=True)
    ip: IPvAnyAddress | None = Field(None, exclude=True)


class AccessTokenClaim(TokenBase):
    type: TokenType = TokenType.ACCESS
    is_admin: bool


class RefreshTokenClaim(TokenBase):
    type: TokenType = TokenType.REFRESH
    ip: IPvAnyAddress


class WebToken(BaseSchema):
    access_token: str
    expires_in: int
    token_type: str = "bearer"
    refresh_token: str
    refresh_token_expires_in: int


class OTPTokenClaim(TokenBase):
    type: TokenType = TokenType.OTP
    ip: IPvAnyAddress


class OTPSaltedHash(OTPTokenClaim):
    salt: str
    hash: str


class OTPWebToken(BaseSchema):
    otp_access_token: str
    expires_in: int
    token_type: str = "bearer"


class ResetPasswordTokenClaim(TokenBase):
    type: TokenType = TokenType.RESET_PASSWORD
    ip: IPvAnyAddress
