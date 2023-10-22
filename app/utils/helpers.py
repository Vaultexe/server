import datetime as dt
from typing import Any


def to_str(value: Any) -> str | None:
    """Convert value to string"""
    return str(value) if value is not None else None


def to_timestamp(value: dt.datetime | None) -> int | None:
    """Convert datetime to timestamp"""
    return int(value.timestamp()) if value is not None else None
