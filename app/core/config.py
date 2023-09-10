from enum import Enum

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

    @property
    def is_dev(self) -> bool:
        return self.ENV == Env.dev

    @property
    def is_prod(self) -> bool:
        return self.ENV == Env.prod


settings = Settings()
