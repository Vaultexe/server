from enum import Enum
from typing import Self

from app import schemas


def rt_key_gen(id: str) -> str:
    return f"refresh_token:{id}"


def otp_at_key_gen(id: str) -> str:
    return f"otp_salted_hash:{id}"


def reset_pass_key_gen(token: str) -> str:
    return f"reset_password_token:{token}"


class KeyGen(Enum):
    """
    Enum for the different types of key builders.
    """

    REFRESH_TOKEN = rt_key_gen
    OTP_SALTED_HASH = otp_at_key_gen
    RESET_PASSWORD_TOKEN = reset_pass_key_gen

    def __call__(self, s: str) -> str:
        """Factory method for the key builders"""
        return self.value(s)

    @classmethod
    def from_token(cls, token_cls: type[schemas.TokenBase]) -> Self:
        key_gen = {
            schemas.RefreshTokenClaim: cls.REFRESH_TOKEN,
            schemas.OTPSaltedHashClaim: cls.OTP_SALTED_HASH,
        }.get(token_cls, None)

        if key_gen is None:
            raise ValueError(f"Invalid token type: {token_cls}")

        return key_gen
