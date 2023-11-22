from collections.abc import Callable

import pytest

from app.cache.key_gen import KeyGen
from app.schemas import AccessTokenClaim, OTPSaltedHashClaim, RefreshTokenClaim, TokenBase


@pytest.mark.parametrize(
    "token_cls, expected",
    [
        (RefreshTokenClaim, KeyGen.REFRESH_TOKEN),
        (OTPSaltedHashClaim, KeyGen.OTP_SALTED_HASH),
    ],
)
def test_from_token(token_cls: type[TokenBase], expected: KeyGen):
    assert KeyGen.from_token(token_cls) == expected

@pytest.mark.parametrize(
    "token_cls",
    [
        TokenBase,
        AccessTokenClaim,
    ],
)
def test_from_token_invalid(token_cls: type[TokenBase]):
    with pytest.raises(ValueError):
        KeyGen.from_token(token_cls)


@pytest.mark.parametrize(
    "key_gen, key",
    [
        (KeyGen.OTP_SALTED_HASH, "otp_shash"),
        (KeyGen.REFRESH_TOKEN, "refresh_token"),
        (KeyGen.RESET_PASSWORD_TOKEN, "reset_pwd_token"),
    ]
)
def test_key_gen(
    key_gen: KeyGen,
    key: str,
):
    assert key_gen(key) == f"{key_gen.value}:{key}"


@pytest.mark.parametrize(
    "key_gen, key",
    [
        (KeyGen.OTP_SALTED_HASH, "otp_shash"),
        (KeyGen.REFRESH_TOKEN, "refresh_token"),
        (KeyGen.RESET_PASSWORD_TOKEN, "reset_pwd_token"),
    ]
)
def test_key_gen_hash(
    key_gen: KeyGen,
    key: str,
    is_md5: Callable[[str], bool],
):
    assert is_md5(key_gen(key, hash_key=True))
