import uuid

from app.cache.client import AsyncRedisClient
from app.cache.key_gen import KeyGen
from app.core.config import settings
from app.schemas import OTPSaltedHashClaim, RefreshTokenClaim


class CacheRepo:
    """Cache repo"""

    async def get_refresh_token_claim(
        self,
        rc: AsyncRedisClient,
        *,
        user_id: uuid.UUID,
    ) -> RefreshTokenClaim | None:
        """Get refresh token claim from redis"""
        key = KeyGen.REFRESH_TOKEN(user_id)
        rt_claim = await rc.get(key)
        return RefreshTokenClaim.model_validate(rt_claim) if rt_claim else None

    async def get_otp_sh_claim(
        self,
        rc: AsyncRedisClient,
        *,
        user_id: uuid.UUID,
    ) -> OTPSaltedHashClaim | None:
        """Get otp salted hash claim from redis"""
        key = KeyGen.OTP_SALTED_HASH(user_id)
        otp_sh_claim = await rc.get(key)
        return OTPSaltedHashClaim.model_validate(otp_sh_claim) if otp_sh_claim else None

    async def save_otp_sh_claim(
        self,
        rc: AsyncRedisClient,
        *,
        user_id: uuid.UUID,
        otp_sh_claim: OTPSaltedHashClaim,
    ) -> bool:
        """Cache otp salted hash claim in redis"""
        return await rc.set(
            KeyGen.OTP_SALTED_HASH(user_id),
            otp_sh_claim.model_dump(),
            ttl=settings.OTP_EXPIRE_SECONDS,
        )

    async def delete_otp_sh_claim(
        self,
        rc: AsyncRedisClient,
        *,
        user_id: uuid.UUID,
    ) -> bool:
        """Delete otp salted hash claim from redis"""
        key = KeyGen.OTP_SALTED_HASH(user_id)
        return await rc.delete(key)

    async def save_refresh_token_claim(
        self,
        rc: AsyncRedisClient,
        *,
        user_id: uuid.UUID,
        rt_claim: RefreshTokenClaim,
        reset_ttl: bool = False,
    ) -> bool:
        """
        Cache refresh token claim.

        The refresh token claim is cached for the duration of a specified ttl.
        When requesting resources, the access token jtis are compared to the refresh token jti.
        So if the refresh token has expired, the access token will still be valid until it expires.

        During refresh token rotation, the ttl is decreased to the remaining time of the refresh token.
        However if user logs in before the refresh token expires, the ttl is reset to the refresh token's ttl.
        This can be done by setting the :reset_ttl to True.

        Args:
            rc (RedisClient | None, optional): Redis client. Defaults to None.
            user_id (int): The user's ID
            rt_claim (schemas.RefreshTokenClaim): The refresh token claim
            reset_ttl (bool, optional): Reset ttl to refresh token's ttl. Defaults to False.

        Returns:
            bool: True if successful, False otherwise.
        """
        rt_key = KeyGen.REFRESH_TOKEN(user_id)

        if not reset_ttl:
            rt_exists = await rc.exists(rt_key)
            if rt_exists:
                return await rc.set(rt_key, rt_claim, keepttl=True)

        ttl = settings.REFRESH_TOKEN_EXPIRE_SECONDS

        return await rc.set(rt_key, rt_claim, ttl=ttl)


repo = CacheRepo()
