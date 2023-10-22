from enum import Enum

from pydantic import EmailStr, field_validator
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings


class Env(str, Enum):
    dev = "dev"
    prod = "prod"


class Settings(BaseSettings):
    """App global settings"""

    # APP
    ENV: Env = Env.dev
    DOMAIN: str
    BACKEND_DOMAIN: str
    PROJECT_NAME: str

    # Admin
    SUPERUSER_EMAIL: EmailStr

    # SECURITY
    OTP_EXPIRE_SECONDS: int
    OTP_LENGTH: int
    JWT_HASHING_ALGORITHM: str = "HS256"
    JWT_SECRET_KEY: str
    REFRESH_TOKEN_EXPIRE_SECONDS: int
    ACCESS_TOKEN_EXPIRE_SECONDS: int

    # SMTP
    EMAILS_ENABLED: bool
    SENDGRID_API_KEY: str
    EMAILS_FROM: EmailStr
    EMAILS_STATUS_TTL: int = 60 * 60 * 24  # 1 day

    # DB
    USE_PGBOUNCER: bool = False
    POSTGRES_URI: str | None
    PGBOUNCER_URI: str | None
    DATABASE_DSN: str | None = None

    # Cache
    REDIS_URI: str

    @field_validator("DATABASE_DSN", mode="before")
    def assemble_db_dsn(cls, v, info: ValidationInfo) -> str:
        """Assemble database DSN from environment variables"""
        if info.data["USE_PGBOUNCER"]:
            return info.data["PGBOUNCER_URI"]
        return info.data["POSTGRES_URI"]

    @property
    def is_dev(self) -> bool:
        return self.ENV == Env.dev

    @property
    def is_prod(self) -> bool:
        return self.ENV == Env.prod

    @property
    def email_enabled(self) -> bool:
        return self.is_prod or self.EMAILS_ENABLED


settings = Settings()
