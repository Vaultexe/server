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
)


def get_ip(req: Request) -> IPvAnyAddress:
    """Returns the IP address of the client making the request"""
    if ip := req.headers.get("X-Forwarded-For"):
        return IPvAnyAddress(ip.split(",", 1)[0])
    return IPvAnyAddress(req.client.host)  # type: ignore


def get_user_agent(req: Request) -> str:
    """Returns the user agent of the client making the request"""
    return req.headers.get("User-Agent", "")


ReqIpDep = Annotated[IPvAnyAddress, Depends(get_ip)]
ReqUserAgentDep = Annotated[str, Depends(get_user_agent)]

DeviceIDCookieDep = Annotated[str | None, Cookie(alias=CookieKey.DEVICE_ID)]
OTPTokenCookieDep = Annotated[str | None, Cookie(alias=CookieKey.OTP_TOKEN)]
AccessTokenCookieDep = Annotated[str | None, Cookie(alias=CookieKey.ACCESS_TOKEN)]
RefreshTokenCookieDep = Annotated[str | None, Cookie(alias=CookieKey.REFRESH_TOKEN)]


async def get_curr_device(
    db: DbDep,
    device_id: DeviceIDCookieDep = None,
) -> models.Device | None:
    """
    Returns the device making the request
    if it was registered in the system (verified or not)
    else None
    """
    if device_id:
        device = await repo.device.get(db, id=device_id)
        return device
    return None


async def get_curr_verified_device(
    device: Annotated[models.Device | None, Depends(get_curr_device)],
) -> models.Device | None:
    """
    Returns the device making the request
    if it was registered & verified in the system
    else None
    """
    if device and device.is_verified:
        return device
    return None


ReqDeviceDep = Annotated[models.Device | None, Depends(get_curr_device)]
ReqVerifiedDeviceDep = Annotated[models.Device | None, Depends(get_curr_verified_device)]


async def get_current_user(
    rc: AsyncRedisClientDep,
    db: DbDep,
    req_ip: ReqIpDep,
    req_device_id: DeviceIDCookieDep = None,
    token: AccessTokenCookieDep = None,
) -> models.User:
    """
    Returns the user making the request
    with the given access token
    if it is still valid
    and with a verified device
    """
    if not token:
        raise AuthenticationException

    is_verified_device = await repo.device.is_verified(db, id=req_device_id)

    if not is_verified_device:
        raise AuthenticationException

    at_claim = AccessTokenClaim.from_encoded(token)

    rt_claim = await cache.repo.get_token(
        rc=rc,
        key=str((at_claim.sub, req_device_id)),
        token_cls=RefreshTokenClaim,
    )

    if (
        rt_claim is None \
        or at_claim.jti != rt_claim.jti \
        or str(req_ip) != str(rt_claim.ip)
    ):  # fmt: off
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


async def get_refresh_user(
    db: DbDep,
    req_ip: ReqIpDep,
    rc: AsyncRedisClientDep,
    req_device_id: DeviceIDCookieDep = None,
    access_token: AccessTokenCookieDep = None,
    refresh_token: RefreshTokenCookieDep = None,
) -> models.User:
    """
    Returns the user making the request
    with the given refresh and access tokens
    if refresh token is still valid
    but access token is expired
    """
    if not refresh_token or not access_token:
        raise AuthenticationException

    is_verified_device = await repo.device.is_verified(db, id=req_device_id)

    if not is_verified_device:
        raise AuthenticationException

    rt_claim = RefreshTokenClaim.from_encoded(refresh_token)
    at_claim = AccessTokenClaim.from_encoded(access_token, allow_expired=True)

    if (
        at_claim.jti != rt_claim.jti \
        or at_claim.sub != rt_claim.sub
    ):  # fmt: off
        raise AuthenticationException

    validator_rt = await cache.repo.get_token(
        rc=rc,
        key=str((rt_claim.sub, req_device_id)),
        token_cls=RefreshTokenClaim,
    )

    if (
        validator_rt is None \
        or rt_claim.jti != validator_rt.jti \
        or str(req_ip) != str(rt_claim.ip)
    ):  # fmt: off
        raise AuthenticationException

    user = await repo.user.get(db, id=rt_claim.sub)

    if not user or not user.is_active:
        raise AuthenticationException

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
    if not token:
        raise AuthenticationException

    otp_claim = OTPTokenClaim.from_encoded(token)

    user = await repo.user.get(db, id=str(otp_claim.sub))

    if not user:
        raise AuthenticationException

    return user


OAuth2PasswordRequestFormDep = Annotated[OAuth2PasswordRequestForm, Depends()]
OTPUserDep = Annotated[models.User, Depends(get_otp_user)]
RefreshUserDep = Annotated[models.User, Depends(get_refresh_user)]
UserDep = Annotated[models.User, Depends(get_current_user)]
AdminDep = Annotated[models.User, Depends(get_current_admin)]
