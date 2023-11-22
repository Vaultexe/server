import json

import pytest

from app.core.config import settings
from app.core.security import (
    decode_token,
    encode_token,
    generate_otp,
    get_salted_hash,
    hash_pwd,
    sha256_hash,
    verify_pwd,
    verify_salted_hash,
)
from app.schemas.token import AccessTokenClaim
from app.utils.exceptions import AuthenticationException, TokenExpiredException


def test_encode_token(mock_access_token_claim: AccessTokenClaim):
    token = encode_token(mock_access_token_claim.model_dump())
    assert isinstance(token, str)


def test_decode_token(mock_access_token_claim: AccessTokenClaim):
    token = encode_token(mock_access_token_claim.model_dump())
    decoded_token = decode_token(token)
    assert decoded_token == mock_access_token_claim.model_dump()


def test_decode_token_allow_expired(mock_expired_access_token_claim: AccessTokenClaim):
    token = encode_token(mock_expired_access_token_claim.model_dump())
    decoded_token = decode_token(token, allow_expired=True)
    assert decoded_token == mock_expired_access_token_claim.model_dump()


def test_decode_token_expired(mock_expired_access_token_claim: AccessTokenClaim):
    token = encode_token(mock_expired_access_token_claim.model_dump())
    with pytest.raises(TokenExpiredException):
        decode_token(token)


def test_decode_token_invalid():
    with pytest.raises(AuthenticationException):
        decode_token(json.dumps({"invalid": "token"}))


def test_generate_otp():
    otp = generate_otp()
    assert len(otp) == settings.OTP_LENGTH
    assert otp.isdigit()


def test_get_salted_hash():
    salt, hash = get_salted_hash("password")
    assert isinstance(salt, str)
    assert isinstance(hash, str)


def test_verify_salted_hash():
    salt, hash = get_salted_hash("password")
    result = verify_salted_hash("password", salt, hash)
    assert result is True


def test_verify_salted_hash_invalid():
    salt, hash = get_salted_hash("password")
    result = verify_salted_hash("wrong_password", salt, hash)
    assert result is False


def test_sha256_hash():
    data = b"hello"
    hashed_data = sha256_hash(data)
    assert isinstance(hashed_data, str)


def test_hash_pwd():
    password = "password"
    hashed_password = hash_pwd(password)
    assert isinstance(hashed_password, str)


def test_verify_pwd():
    password = "password"
    hashed_password = hash_pwd(password)
    result = verify_pwd(password, hashed_password)
    assert result is True


def test_verify_pwd_invalid():
    password = "password"
    hashed_password = hash_pwd(password)
    result = verify_pwd("wrong_password", hashed_password)
    assert result is False
