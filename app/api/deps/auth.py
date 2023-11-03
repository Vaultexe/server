import datetime as dt
from typing import Annotated

from fastapi import Cookie, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import IPvAnyAddress

from app import cache, models
from app.api.deps.cache import AsyncRedisClientDep
from app.api.deps.db import DbDep
from app.db import repos as repo
from app.schemas.enums import CookieKey
from app.schemas.token import AccessTokenClaim, OTPTokenClaim, RefreshTokenClaim
from app.utils.exceptions import (
    AuthenticationException,
    AuthorizationException,
    TokenExpiredException,
)


def get_ip(req: Request) -> IPvAnyAddress:
    """Returns the IP address of the client making the request"""
    if ip := req.headers.get("X-Forwarded-For"):
        return ip.split(",", 1)[0]  # type: ignore
    return req.client.host  # type: ignore


def get_user_agent(req: Request) -> str:
    """Returns the user agent of the client making the request"""
    return req.headers.get("User-Agent", "")


ReqIpDep = Annotated[IPvAnyAddress, Depends(get_ip)]
ReqUserAgentDep = Annotated[str, Depends(get_user_agent)]

DeviceIDCookieDep = Annotated[str | None, Cookie(alias=CookieKey.DEVICE_ID)]
OTPTokenCookieDep = Annotated[str | None, Cookie(alias=CookieKey.OTP_TOKEN)]
AccessTokenCookieDep = Annotated[str | None, Cookie(alias=CookieKey.ACCESS_TOKEN)]


async def get_current_device(
    db: DbDep,
    device_id: DeviceIDCookieDep = None,
) -> models.Device | None:
    """
    Returns the device making the request
    if it was registered & verified in the system
    else None
    """
    if device_id:
        device = await repo.device.get(db, id=device_id)
        if device and device.is_verified:
            return device
    return None


async def get_current_user(
    rc: AsyncRedisClientDep,
    db: DbDep,
    req_ip: ReqIpDep,
    token: AccessTokenCookieDep = None,
) -> models.User:
    """
    Returns the user making the request
    with the given access token
    if it is still valid
    """
    at_claim = AccessTokenClaim.from_encoded(token)

    rt_claim = await cache.repo.get_token(
        rc=rc,
        key=at_claim.sub,
        token_cls=RefreshTokenClaim,
    )

    if rt_claim is None or at_claim.jti != rt_claim.jti or str(req_ip) != str(rt_claim.ip):
        raise AuthenticationException

    user = await repo.user.get(db, id=at_claim.sub)

    if not user or not user.is_active:
        raise AuthenticationException

    return user


async def get_current_admin(
    user: Annotated[models.User, Depends(get_current_user)],
) -> models.User:
    """
    Returns the user making the request
    if they are an admin
    """
    if not user.is_admin:
        raise AuthorizationException
    return user


async def get_otp_user(
    db: DbDep,
    token: OTPTokenCookieDep = None,
) -> models.User:
    """
    Returns the user making the request
    with the given OTP token
    if it is still valid
    """
    otp_claim = OTPTokenClaim.from_encoded(token)

    if otp_claim.exp < dt.datetime.now(dt.UTC):
        raise TokenExpiredException

    user = await repo.user.get(db, id=otp_claim.sub)

    if not user:
        raise AuthenticationException

    return user


ReqDeviceDep = Annotated[models.Device | None, Depends(get_current_device)]
OAuth2PasswordRequestFormDep = Annotated[OAuth2PasswordRequestForm, Depends()]
OTPUserDep = Annotated[models.User, Depends(get_otp_user)]
UserDep = Annotated[models.User, Depends(get_current_user)]
AdminDep = Annotated[models.User, Depends(get_current_admin)]
