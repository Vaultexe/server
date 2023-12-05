import uuid
from typing import Annotated

import rq
from fastapi import APIRouter, Body, Path, Response, status
from pydantic import IPvAnyAddress
from sqlalchemy.ext.asyncio import AsyncSession

from app import cache, models, schemas
from app.api.deps import (
    AsyncRedisClientDep,
    DbDep,
    DeviceIDCookieDep,
    MQHigh,
    OAuth2PasswordRequestFormDep,
    OTPUserDep,
    RefreshUserDep,
    ReqIpDep,
    ReqUserAgentDep,
    ReqVerifiedDeviceDep,
)
from app.cache.client import AsyncRedisClient
from app.cache.key_gen import KeyGen
from app.core import security, tokens
from app.core.config import settings
from app.db import repos as repo
from app.schemas.enums import CookieKey
from app.utils.emails import send_otp_email
from app.utils.exceptions import (
    AuthenticationException,
    AuthorizationException,
    EntityNotFoundException,
    InvalidOTPException,
    TokenExpiredException,
    UnverifiedEmailException,
    UserAlreadyActiveException,
)

router = APIRouter()


@router.post("/register/{registration_token}")
async def register(
    db: DbDep,
    req_ip: ReqIpDep,
    req_user_agent: ReqUserAgentDep,
    registration_token: Annotated[str, Path(...)],
    password: Annotated[
        str,
        Body(
            ...,
            description="Double KDF hash of master password",
        ),
    ],
    res: Response,
) -> Response:
    """
    ## Register by setting a new password

    ## Prerequisites
    * User account invited by admin
    * User has not been activated account yet

    ## Overview
    * Validates registration token
    * Validates user account
    * Hashes & sets the new user password (already double KDF hashed by client)
    * Activates user account
    * Invalidates token
    """
    invitation = await repo.invitation.get_by_token(db, token=registration_token)

    if not invitation or not invitation.is_valid or invitation.is_expired:
        raise AuthorizationException

    invitee = await repo.user.get(db, id=invitation.invitee_id)

    if not invitee:
        raise EntityNotFoundException(models.User)

    if invitee.is_active:
        raise UserAlreadyActiveException

    invitee.update_password(password).verify_email().activate()

    await repo.invitation.invalidate_tokens(db, user_id=invitee.id)

    await db.commit()

    await register_new_device(
        db=db,
        res=res,
        ip=req_ip,
        verified=True,
        user_id=invitee.id,
        user_agent=req_user_agent,
    )

    res.status_code = status.HTTP_200_OK
    return res


@router.post(
    "/oauth2",
    responses={
        status.HTTP_200_OK: {
            "description": "User authenticated successfully",
        },
        status.HTTP_202_ACCEPTED: {
            "description": "User authenticated, 2fa required",
        },
    },
)
async def oauth2_login(
    db: DbDep,
    mq: MQHigh,
    req_ip: ReqIpDep,
    rc: AsyncRedisClientDep,
    req_user_agent: ReqUserAgentDep,
    req_device: ReqVerifiedDeviceDep,
    form_data: OAuth2PasswordRequestFormDep,
    res: Response,
) -> Response:
    """
    ## OAuth2 login

    ## Login flows
    * **Login with a new device/browser**
    If the user has not logged in with the current device/browser before,
    the user will be prompted to enter their 2fa code sent to their email.
    A new device is identified if the device_id cookie is not present
    or if the user agent has changed.

    * **Normal Login**
    No 2fa required. user is logging in with a previously
    registered device/browser.

    ## Overview
    * Extracts device_id from cookie & user agent from request header
    * Validates user credentials
    * Registers new device if user is logging in with a new device/browser
    * Returns (access & refresh tokens) or (otp token) with corresponding status code

    ## Cookies

    ### New device/browser login
    * **vaultexe_device_id**
    * **vaultexe_otp_token**

    ### Normal login
    * **vaultexe_access_token**
    * **vaultexe_refresh_token**
    """
    user = await repo.user.authenticate(
        db,
        email=form_data.username,
        password=form_data.password,
    )

    if not user or not user.is_active:
        raise AuthenticationException

    if settings.is_prod and not user.email_verified:
        raise UnverifiedEmailException

    # If device/browser & user agent has been registered before
    if req_device and req_device.user_agent == req_user_agent:
        req_device.refresh_last_login(ip=req_ip)
        await db.commit()
        return await grant_web_token(rc=rc, user=user, ip=req_ip, device_id=req_device.id, res=res)
    else:
        await register_new_device(
            db=db,
            res=res,
            ip=req_ip,
            user_id=user.id,
            user_agent=req_user_agent,
        )
        return await grant_autherization_code(rc=rc, mq=mq, user=user, ip=req_ip, res=res)


@router.post("/refresh")
async def refresh(
    res: Response,
    req_ip: ReqIpDep,
    user: RefreshUserDep,
    rc: AsyncRedisClientDep,
    req_device_id: DeviceIDCookieDep = None,
) -> Response:
    """
    ## Refresh access token

    ## Prerequisites
    * User has been authenticated via oauth2 login
    * User Device/Browser is registered & verified

    ## Overview
    * Validates refresh & the expired access tokens
    * Returns new access & refresh tokens

    ## Cookies
    * **vaultexe_access_token**
    * **vaultexe_refresh_token**
    """
    if not req_device_id:
        raise AuthenticationException
    return await grant_web_token(
        rc=rc,
        res=res,
        user=user,
        ip=req_ip,
        is_refresh=True,
        device_id=req_device_id,
    )


@router.post("/otp")
async def otp_login(
    db: DbDep,
    ip: ReqIpDep,
    res: Response,
    user: OTPUserDep,
    rc: AsyncRedisClientDep,
    otp: Annotated[str, Body(...)],
    req_device_id: DeviceIDCookieDep = None,
) -> Response:
    """
    ## OTP login

    ## Prerequisites
    * User has been authenticated via oauth2 login

    ## Overview
    * Validates otp
    * Delete cached otp hash claim
    * Returns access & refresh tokens

    ## Cookies
    * **vaultexe_access_token**
    * **vaultexe_refresh_token**
    """
    if not req_device_id:
        raise AuthenticationException

    otp_sh_claim = await cache.repo.get_token(
        rc,
        key=str(user.id),
        token_cls=schemas.OTPSaltedHashClaim,
    )

    if not otp_sh_claim:
        raise TokenExpiredException

    is_valid_otp = security.verify_salted_hash(otp, otp_sh_claim.salt, otp_sh_claim.hash)

    if not is_valid_otp:
        raise InvalidOTPException

    if otp_sh_claim.ip != ip:
        raise AuthenticationException

    await cache.repo.delete_token(rc, key=str(user.id), key_gen=KeyGen.OTP_SALTED_HASH)

    await repo.device.verify(db, id=req_device_id)
    await db.commit()

    res.delete_cookie(key=CookieKey.OTP_TOKEN)

    return await grant_web_token(rc=rc, user=user, ip=ip, device_id=req_device_id, res=res)


async def grant_web_token(
    *,
    rc: AsyncRedisClient,
    user: models.User,
    ip: IPvAnyAddress,
    device_id: str,
    res: Response,
    is_refresh: bool = False,
) -> Response:
    """
    ## Generates & returns access & refresh tokens

    ## flow
    An access token and a refresh token will be generated and sent with the response.
    The refresh token claim will be stored in redis with a specified ttl.
    Even if there was a previous active refresh token
    The refresh token claim will contain the same jti as the access token claim.
    This will ensure that the currently used access token was generated along with the refresh token.
    Eventually when a user requests a new access token, a new refresh token will be generated as well.
    (aka: refresh token rotation)

    Args:
        is_refresh (bool, optional): If true, the refresh token will be cached but maintain its ttl.
    """
    _, at, rt_claim, rt = tokens.create_web_tokens(
        ip=ip,
        subject=user.id,
        is_admin=user.is_admin,
    )

    await cache.repo.save_token_claim(
        rc,
        token_claim=rt_claim,
        key=str((str(user.id), device_id)),
        keep_ttl=is_refresh,
    )

    res.status_code = status.HTTP_200_OK

    res.set_cookie(
        key=CookieKey.REFRESH_TOKEN,
        value=rt,
        httponly=True,
        secure=settings.is_prod,
        expires=rt_claim.exp,
    )

    # keep access token for the same duration as the refresh token
    # this is because expired access tokens are used along with the refresh tokenduring token rotation
    res.set_cookie(
        key=CookieKey.ACCESS_TOKEN,
        value=at,
        secure=settings.is_prod,
        expires=rt_claim.exp,
    )

    return res


async def grant_autherization_code(
    *,
    mq: rq.Queue,
    rc: AsyncRedisClient,
    user: models.User,
    ip: IPvAnyAddress,
    res: Response,
) -> Response:
    """
    ## Generates & emails an authorization code to the user

    ## flow
    A jwt token will be generated and sent with the response.
    Another token will be generated called otp salted hash and stored in redis with a specified ttl.
    This token will contain the same jti as the jwt token sent with the response.
    It will also contain the salted hash of the otp for future verification.

    The otp access token will be sent along with the otp from the client.
    This access token will be used to ensure that the 2fa process is done
    via the same device/browser that initiated the process and within a specified time frame.
    """
    otp = security.generate_otp()

    otp_sh_claim, otpt_claim, otpt = tokens.create_otp_tokens(
        ip=ip,
        otp=otp,
        subject=user.id,
    )

    await cache.repo.save_token_claim(rc, key=str(user.id), token_claim=otp_sh_claim)

    email_payload = schemas.OTPEmailPayload(
        otp=otp,
        to=user.email,
        expires_at=otpt_claim.exp,
    )

    mq.enqueue_call(
        func=send_otp_email,
        args=(email_payload,),
        retry=rq.Retry(max=2),
        result_ttl=settings.EMAILS_STATUS_TTL,
    )

    res.status_code = status.HTTP_202_ACCEPTED

    res.set_cookie(
        key=CookieKey.OTP_TOKEN,
        value=otpt,
        httponly=True,
        secure=settings.is_prod,
        expires=otpt_claim.exp,
    )

    return res


async def register_new_device(
    *,
    db: AsyncSession,
    user_id: uuid.UUID,
    ip: IPvAnyAddress,
    user_agent: str,
    verified: bool = False,
    res: Response,
) -> None:
    """
    Registers a new device

    Sets a cookie with the device id
    """
    new_device = schemas.DeviceCreate(
        ip=ip,
        user_id=user_id,
        is_verified=verified,
        user_agent=user_agent,
    )

    device = await repo.device.create(db, obj_in=new_device)

    await db.commit()
    await db.refresh(device, ["id"])

    await repo.device.clear_redundant_devices(
        db=db,
        ip=ip,
        user_id=user_id,
        user_agent=user_agent,
        exclude_id=device.id,
    )

    await db.commit()

    res.set_cookie(
        key=CookieKey.DEVICE_ID,
        value=device.id,
        httponly=True,
        secure=settings.is_prod,
    )
