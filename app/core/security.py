import hashlib
import secrets
import string
from typing import Any

import argon2
import bcrypt
from jose import exceptions as jwt_errors
from jose import jwt as jwt_lib

from app.core.config import settings
from app.utils.exceptions import AuthenticationException, TokenExpiredException


def encode_token(claim: dict[str, Any]) -> str:
    """Encode a JWT token"""
    return jwt_lib.encode(
        claim,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_HASHING_ALGORITHM,
    )


def decode_token(token: str, *, allow_expired: bool = False) -> dict[str, Any]:
    """
    Decode a JWT token.

    Auto verifies:
        - The signature
        - The expiration time
        - The audience
        - The issuer

    Returns:
        dict[str, Any]: The decoded JWT token claims

    Raises:
        TokenExpiredException (401): If the token is expired
        AuthenticationError (401): If the token is invalid
    """
    try:
        decoded_token = jwt_lib.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=settings.JWT_HASHING_ALGORITHM,
            options={"verify_exp": not allow_expired},
        )
    except jwt_errors.ExpiredSignatureError:
        raise TokenExpiredException
    except jwt_errors.JWTError:
        raise AuthenticationException

    return decoded_token


def generate_otp() -> str:
    """Generate a otp token."""
    return "".join(secrets.choice(string.digits) for _ in range(settings.OTP_LENGTH))


def get_salted_hash(t: str) -> tuple[str, str]:
    """
    Get a salted hash of a text.

    Returns:
        tuple[str, str]: [salt, hash]
    """
    salt = bcrypt.gensalt()
    hash = sha256_hash(salt + t.encode())
    return salt.decode(), hash


def verify_salted_hash(t: str, salt: str, hash: str) -> bool:
    """
    Verify a salted hash of a text.

    Returns:
        bool: True if the token is valid
    """
    return hash == sha256_hash((salt + t).encode())


def sha256_hash(data: bytes) -> str:
    """Get a sha256 hash of a string"""
    return hashlib.sha256(data, usedforsecurity=False).hexdigest()


def hash_pwd(pwd: str) -> str:
    """
    Hash a password

    Uses argon2id algorithm, it embeds the salt in the hash
    """
    return argon2.PasswordHasher().hash(pwd)


def verify_pwd(pwd: str, hash: str) -> bool:
    """
    Verify a password

    Uses argon2id algorithm, it embeds the salt in the hash
    """
    try:
        argon2.PasswordHasher().verify(hash, pwd)
    except Exception:
        return False
    else:
        return True
