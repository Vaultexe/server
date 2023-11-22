import datetime as dt
from typing import AnyStr

import pytest

from app.utils.helpers import to_str, to_timestamp


@pytest.mark.parametrize(
    "input, expected",
    [
        (123, "123"),
        (12.34, "12.34"),
        (None, None),
        ("test", "test"),
        (True, "True"),
    ],
)
def test_to_str(input: AnyStr, expected: str):
    assert to_str(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    [
        (dt.datetime(2022, 1, 1), dt.datetime(2022, 1, 1).timestamp()),
        (None, None),
        (dt.datetime(2022, 12, 31, 23, 59, 59), dt.datetime(2022, 12, 31, 23, 59, 59).timestamp()),
    ],
)
def test_to_timestamp(input: dt.datetime, expected: int):
    assert to_timestamp(input) == expected
