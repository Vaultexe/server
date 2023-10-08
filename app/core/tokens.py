import datetime as dt
import uuid

from pydantic import IPvAnyAddress

from app.core import security
from app.core.config import settings
from app.schemas import (
    AccessTokenClaim,
    OTPSaltedHash,
    OTPTokenClaim,
    RefreshTokenClaim,
)


def create_web_tokens(
    *,
    subject: uuid.UUID | str,
    ip: IPvAnyAddress,
    is_admin: bool,
    at_ttl: int = settings.ACCESS_TOKEN_EXPIRE_SECONDS,
    rt_ttl: int = settings.REFRESH_TOKEN_EXPIRE_SECONDS,
) -> tuple[AccessTokenClaim, str, RefreshTokenClaim, str]:
    """
    Create [access_token, refresh_token] pair.

    Args:
        subject (uuid.UUID | str): The user's UUID
        ip (IPvAnyAddress): The IP address of the user
        is_admin (bool): Whether the user is an admin
        at_ttl (int, optional): The access token time to live in seconds
        rt_ttl (int, optional): The refresh token time to live in seconds

    Returns:
        tuple[AccessTokenClaim, str, RefreshTokenClaim, str]: [at_claim, at, rt_claim, rt]
    """
    jti, iat = uuid.uuid4(), dt.datetime.now(dt.UTC)

    at_exp = iat + dt.timedelta(seconds=at_ttl)
    rt_exp = iat + dt.timedelta(seconds=rt_ttl)

    at_claim = AccessTokenClaim(jti=jti, sub=subject, is_admin=is_admin, iat=iat, exp=at_exp)
    rt_claim = RefreshTokenClaim(jti=jti, sub=subject, ip=ip, iat=iat, exp=rt_exp)

    at = security.encode_token(at_claim.model_dump())
    rt = security.encode_token(rt_claim.model_dump())

    return at_claim, at, rt_claim, rt


def create_otp_tokens(
    *,
    subject: uuid.UUID | str,
    ip: IPvAnyAddress,
    otp: str,
    otpt_ttl: int = settings.OTP_EXPIRE_SECONDS,
) -> tuple[OTPSaltedHash, OTPTokenClaim, str]:
    """
    Create an OTP token

    It is sent along with the OTP code to the server
    to ensure that the OTP is used from the same device that requested it.
    """
    salt, hash = security.get_salted_hash(otp)

    jti, iat = uuid.uuid4(), dt.datetime.now(dt.UTC)
    exp = iat + dt.timedelta(seconds=otpt_ttl)

    otpt_claim = OTPTokenClaim(jti=jti, sub=subject, ip=ip, iat=iat, exp=exp)
    otp_sh_claim = OTPSaltedHash(jti=jti, sub=subject, ip=ip, iat=iat, exp=exp, salt=salt, hash=hash)

    otpt = security.encode_token(otpt_claim.model_dump())

    return otp_sh_claim, otpt_claim, otpt


def create_reset_pwd_token() -> tuple[str, str]:
    """
    Create a reset password token.

    Returns:
        tuple[str, str]: [reset_token, reset_token_hash]
    """
    reset_token = uuid.uuid4()
    reset_token_hash = security.sha256_hash(reset_token.bytes)
    return reset_token, reset_token_hash
