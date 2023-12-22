from app.cache.client import AsyncRedisClient
from app.core.config import settings
from app.schemas import OTPSaltedHashClaim, RefreshTokenClaim, TokenBase


class CacheRepo:
    """Cache repo"""

    async def save_token_claim(
        self,
        rc: AsyncRedisClient,
        *,
        key: str,
        token_claim: TokenBase,
        keep_ttl: bool = False,
    ) -> bool:
        """
        Cache token claim.

        The token claim is cached for its corresponding ttl.

        If the keep_ttl is set to True, the ttl is not changed when the token is updated.
        However if the token is not found in the cache, the ttl is set to the token's ttl.

        If the hash_key is set to True, the key will be md5 hashed before being cached.

        Returns:
            bool: True if successful, False otherwise.
        """
        if keep_ttl:
            exists = await rc.redis.set(
                key,
                token_claim.model_dump_json(),
                xx=True,
                keepttl=True,
            )
            if exists:
                return True

        ttl = self._get_token_type_ttl(type(token_claim))

        return await rc.set(key, token_claim, ttl=ttl)

    async def get_token[T: TokenBase](
        self,
        rc: AsyncRedisClient,
        *,
        key: str,
        token_cls: type[T],
    ) -> T | None:
        """Get token claim"""
        token = await rc.get(key)
        return token_cls.model_validate(token) if token else None

    async def delete_token(
        self,
        rc: AsyncRedisClient,
        *,
        key: str,
    ) -> bool:
        """Delete token claim from redis"""
        return bool(await rc.delete(key))

    async def delete_many_tokens(
        self,
        rc: AsyncRedisClient,
        *,
        keys: list[str],
    ) -> int:
        """Delete many tokens from redis"""
        return await rc.delete_many(keys)

    def _get_token_type_ttl(self, token_cls: type[TokenBase]) -> int:
        ttl = {
            RefreshTokenClaim: settings.REFRESH_TOKEN_EXPIRE_SECONDS,
            OTPSaltedHashClaim: settings.OTP_EXPIRE_SECONDS,
            TokenBase: None,
        }.get(token_cls, None)

        if ttl is None:
            raise ValueError(f"Invalid token type: {token_cls}")

        return ttl


repo = CacheRepo()
