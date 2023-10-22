import datetime as dt
import uuid
from typing import Self

from pydantic import Field, IPvAnyAddress, field_serializer

from app.core import security
from app.schemas import BaseSchema
from app.schemas.enums import TokenType
from app.utils.helpers import to_str, to_timestamp

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

    dates_serilizer = field_serializer("iat", "exp")(to_timestamp)
    ids_serilizer = field_serializer("jti", "sub")(to_str)
    ip_serilizer = field_serializer("ip")(to_str)

    @classmethod
    def from_encoded(cls, token: str) -> Self:
        """Create a token object from an encoded token string"""
        claim = security.decode_token(token)
        return cls.model_validate(claim)


class AccessTokenClaim(TokenBase):
    type: TokenType = TokenType.ACCESS
    is_admin: bool


class RefreshTokenClaim(TokenBase):
    type: TokenType = TokenType.REFRESH
    ip: IPvAnyAddress


class OTPTokenClaim(TokenBase):
    type: TokenType = TokenType.OTP
    ip: IPvAnyAddress


class OTPSaltedHashClaim(OTPTokenClaim):
    salt: str
    hash: str


class ResetPasswordTokenClaim(TokenBase):
    type: TokenType = TokenType.RESET_PASSWORD
    ip: IPvAnyAddress
