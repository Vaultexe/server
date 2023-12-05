from enum import StrEnum, auto
from typing import override


class BaseEnum(StrEnum):
    """
    Base class for all enums
    """


class CipherType(BaseEnum):
    LOGIN = auto()
    NOTE = auto()


class TokenType(BaseEnum):
    ACCESS = auto()
    REFRESH = auto()
    OTP = auto()
    RESET_PASSWORD = auto()


class WorkerQueue(BaseEnum):
    HIGH = auto()
    DEFAULT = auto()
    LOW = auto()


class CookieKey(BaseEnum):
    @override
    def _generate_next_value_(name: str, _, __, ___) -> str:
        """
        Overrides the enum function that generates the next value
        Uses the name as the automatic value, rather than an integer
        See https://docs.python.org/3/library/enum.html#using-automatic-values for reference
        """
        return f"vaultexe_{name.lower()}"

    ACCESS_TOKEN = auto()
    REFRESH_TOKEN = auto()
    OTP_TOKEN = auto()
    DEVICE_ID = auto()


class Op(BaseEnum):
    CREATE = auto()
    UPDATE = auto()
    DELETE = auto()
    SOFT_DELETE = auto()
