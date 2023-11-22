import uuid
from typing import TypedDict

import pytest
from pydantic import IPvAnyAddress

from app.core import security
from app.core.tokens import create_otp_tokens, create_reset_pwd_token, create_web_tokens
from app.schemas import AccessTokenClaim, OTPSaltedHashClaim, OTPTokenClaim, RefreshTokenClaim


class DataDict(TypedDict):
    subject: uuid.UUID
    ip: IPvAnyAddress
    is_admin: bool
    otp : str


@pytest.fixture
def data() -> DataDict:
    return {
        "subject": uuid.uuid4(),
        "ip": IPvAnyAddress("127.0.0.1"),
        "is_admin": False,
        "otp": "123456",
    }


def test_create_web_tokens(data: DataDict) -> None:
    at_claim, at, rt_claim, rt = create_web_tokens(
        subject=data["subject"],
        ip=data["ip"],
        is_admin=data["is_admin"],
    )

    assert isinstance(at_claim, AccessTokenClaim)
    assert isinstance(rt_claim, RefreshTokenClaim)
    assert isinstance(at, str)
    assert isinstance(rt, str)
    assert at_claim.jti == rt_claim.jti
    assert at_claim.sub == rt_claim.sub
    assert at_claim.iat == rt_claim.iat


def test_create_otp_tokens(data: DataDict) -> None:
    otp_salt_claim, otp_token_claim, otp_token = create_otp_tokens(
        otp=data["otp"],
        ip=data["ip"],
        subject=data["subject"],
    )

    assert isinstance(otp_salt_claim, OTPSaltedHashClaim)
    assert isinstance(otp_token_claim, OTPTokenClaim)
    assert isinstance(otp_token, str)
    assert otp_salt_claim.jti == otp_token_claim.jti
    assert otp_salt_claim.sub == otp_token_claim.sub
    assert otp_salt_claim.iat == otp_token_claim.iat


def test_create_reset_password_token() -> None:
    reset_pwd_token, reset_pwd_token_hash = create_reset_pwd_token()

    assert isinstance(reset_pwd_token, uuid.UUID)
    assert isinstance(reset_pwd_token_hash, str)
    assert security.sha256_hash(reset_pwd_token.bytes) == reset_pwd_token_hash
