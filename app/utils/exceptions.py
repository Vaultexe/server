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


class AuthenticationException(TokenExpiredException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
        )
