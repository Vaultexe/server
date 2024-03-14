from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import HTTPException, status

from app.utils.regex import capitalize_first_letter

if TYPE_CHECKING:
    from app.models.base import BaseModel


class TokenExpiredException(HTTPException):
    def __init__(
        self,
        detail: str = "Token has expired",
        headers: dict[str, str] | None = None,
    ) -> None:
        headers = headers or {"WWW-Authenticate": "Bearer"}
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers=headers,
        )


class AuthenticationException(HTTPException):
    def __init__(
        self,
        detail: str = "Authentication failed",
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers=headers,
        )


class AuthorizationException(HTTPException):
    def __init__(
        self,
        detail: str = "Authorization failed",
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            headers=headers,
        )


class InvalidOTPException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid OTP",
        )


class UserAlreadyActiveException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already active",
        )


class UserNotFoundException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )


class UnverifiedEmailException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified",
        )


class EntityNotFoundException(HTTPException):
    def __init__(self, model: type[BaseModel] | str) -> None:
        entity = model if isinstance(model, str) else capitalize_first_letter(model.table_name())
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=f"{entity} not found")


class DuplicateEntityException(HTTPException):
    def __init__(self, model: type[BaseModel] | str) -> None:
        entity = model if isinstance(model, str) else capitalize_first_letter(model.table_name())
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=f"{entity} already exists")


class InvalidFileTypeException(HTTPException):
    def __init__(self, type: str | None = None) -> None:
        expected_statement = f"Expected {type} file" if type else ""
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid file type\n{expected_statement}",
        )
