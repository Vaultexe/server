from fastapi import HTTPException, status


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
    def __init__(self, model: object | str) -> None:
        entity = model.__class__.__name__ if isinstance(model, object) else model
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=f"{entity} not found")


class DuplicateEntityException(HTTPException):
    def __init__(self, model: object | str) -> None:
        entity = model.__class__.__name__ if isinstance(model, object) else model
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=f"{entity} already exists")
