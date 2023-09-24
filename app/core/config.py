from enum import Enum

from pydantic import field_validator
from pydantic_core.core_schema import FieldValidationInfo
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

    # DB
    USE_PGBOUNCER: bool = False
    POSTGRES_URI: str | None
    PGBOUNCER_URI: str | None
    DATABASE_DSN: str | None = None

    @field_validator("DATABASE_DSN", mode="before")
    def assemble_db_dsn(cls, v, info: FieldValidationInfo) -> str:
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


settings = Settings()
