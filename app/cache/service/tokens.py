from app.cache.client import AsyncRedisClient
from app.core.config import settings
from app.schemas import OTPSaltedHashClaim, RefreshTokenClaim, TokenBase


class TokensService:
    async def save(
        self,
        rc: AsyncRedisClient,
        *,
        key: str,
        token_claim: TokenBase,
        keep_ttl: bool = False,
        ttl: int | None = None,
    ) -> int:
        """
        Cache token claim.

        The token claim is cached for its corresponding ttl.

        If the keep_ttl is set to True, the ttl is not changed when the token is updated.
        However if the token is not found in the cache, the ttl is set to the token's ttl.

        Returns:
            int: ttl of the token.
        """
        value = token_claim.model_dump_json()

        if keep_ttl:
            exists = await rc.set(
                key,
                value,
                xx=True,
                keepttl=True,
            )
            if exists:
                return True

        ttl = ttl or self._get_token_type_ttl(type(token_claim))
        return await rc.set(key, value, ex=ttl)

    async def get[T: TokenBase](
        self,
        rc: AsyncRedisClient,
        *,
        key: str,
        token_cls: type[T],
    ) -> T | None:
        """Get token claim"""
        token = await rc.get(key)
        return token_cls.model_validate_json(token) if token else None

    def _get_token_type_ttl(self, token_cls: type[TokenBase]) -> int:
        ttl = {
            RefreshTokenClaim: settings.REFRESH_TOKEN_EXPIRE_SECONDS,
            OTPSaltedHashClaim: settings.OTP_EXPIRE_SECONDS,
            TokenBase: None,
        }.get(token_cls, None)

        if ttl is None:
            raise ValueError(f"Invalid token type: {token_cls}")

        return ttl


tokens = TokensService()
