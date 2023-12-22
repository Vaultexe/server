import pytest
from fastapi import HTTPException

from app.models import User
from app.utils.exceptions import (
    AuthenticationException,
    AuthorizationException,
    DuplicateEntityException,
    EntityNotFoundException,
    InvalidOTPException,
    TokenExpiredException,
    UnverifiedEmailException,
    UserAlreadyActiveException,
    UserNotFoundException,
)


def test_token_expired_exception():
    with pytest.raises(HTTPException) as e:
        raise TokenExpiredException()
    assert e.value.status_code == 401
    assert e.value.detail == "Token has expired"


def test_authentication_exception():
    with pytest.raises(HTTPException) as e:
        raise AuthenticationException()
    assert e.value.status_code == 401
    assert e.value.detail == "Authentication failed"


def test_authorization_exception():
    with pytest.raises(HTTPException) as e:
        raise AuthorizationException()
    assert e.value.status_code == 403
    assert e.value.detail == "Authorization failed"


def test_invalid_otp_exception():
    with pytest.raises(HTTPException) as e:
        raise InvalidOTPException()
    assert e.value.status_code == 401
    assert e.value.detail == "Invalid OTP"


def test_user_already_active_exception():
    with pytest.raises(HTTPException) as e:
        raise UserAlreadyActiveException()
    assert e.value.status_code == 409
    assert e.value.detail == "User already active"


def test_user_not_found_exception():
    with pytest.raises(HTTPException) as e:
        raise UserNotFoundException()
    assert e.value.status_code == 404
    assert e.value.detail == "User not found"


def test_unverified_email_exception():
    with pytest.raises(HTTPException) as e:
        raise UnverifiedEmailException()
    assert e.value.status_code == 403
    assert e.value.detail == "Email not verified"


def test_entity_not_found_exception():
    with pytest.raises(HTTPException) as e:
        raise EntityNotFoundException("TestEntity")
    assert e.value.status_code == 404
    assert e.value.detail == "TestEntity not found"

    with pytest.raises(HTTPException) as e:
        raise EntityNotFoundException(User)
    assert e.value.status_code == 404
    assert e.value.detail == "User not found"


def test_duplicate_entity_exception():
    with pytest.raises(HTTPException) as e:
        raise DuplicateEntityException("TestEntity")
    assert e.value.status_code == 409
    assert e.value.detail == "TestEntity already exists"

    with pytest.raises(HTTPException) as e:
        raise DuplicateEntityException(User)
    assert e.value.status_code == 409
    assert e.value.detail == "User already exists"
