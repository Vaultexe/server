import hashlib
from enum import Enum
from typing import Self

from app import schemas


class KeyGen(Enum):
    """
    Enum for the different types of key builders.
    """

    REFRESH_TOKEN = "refresh_token"  # nosec - this is not a secret (bandit)
    OTP_SALTED_HASH = "otp_shash"  # nosec - this is not a secret (bandit)
    RESET_PASSWORD_TOKEN = "reset_pwd_token"  # nosec - this is not a secret (bandit)

    def __call__(
        self,
        key,
        hash_key: bool = False,
    ) -> str:
        """Factory method for the key builders"""
        cache_key = f"{self.value}:{key}"
        if hash_key:
            return hashlib.md5(
                cache_key.encode(),
                usedforsecurity=False,
            ).hexdigest()
        return cache_key

    @classmethod
    def from_token(
        cls,
        token_cls: type[schemas.TokenBase],
    ) -> Self:
        key_gen = {
            schemas.RefreshTokenClaim: cls.REFRESH_TOKEN,
            schemas.OTPSaltedHashClaim: cls.OTP_SALTED_HASH,
            schemas.TokenBase: None,
        }.get(token_cls, None)

        if key_gen is None:
            raise ValueError(f"Invalid token class: {token_cls}")

        return key_gen
