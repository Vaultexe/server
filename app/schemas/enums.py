from enum import Enum, auto

from typing_extensions import override


class BaseEnum(str, Enum):
    """
    Base class for all enums
    """

    @override
    def _generate_next_value_(name, start, count, last_values) -> str:  # type: ignore
        """
        Overrides the enum function that generates the next value
        Uses the name as the automatic value, rather than an integer
        See https://docs.python.org/3/library/enum.html#using-automatic-values for reference
        """
        return name

    @classmethod
    def as_dict(cls) -> dict:
        return {e.name: e.value for e in cls}


class CipherType(BaseEnum):
    LOGIN = auto()
    NOTE = auto()


class TokenType(BaseEnum):
    ACCESS = auto()
    REFRESH = auto()
    OTP = auto()
    RESET_PASSWORD = auto()
