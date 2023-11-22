from app import cache, core, db, models, schemas, entrypoint, main, utils # noqa

import datetime as dt
import re
import uuid
from collections.abc import Callable

import pytest
from pydantic import IPvAnyAddress

from app.schemas.token import AccessTokenClaim


@pytest.fixture
def mock_access_token_claim() -> AccessTokenClaim:
    return AccessTokenClaim(
        jti=uuid.uuid4(),
        sub="mock_sub",
        iat=dt.datetime.now(dt.UTC),
        exp=dt.datetime.now(dt.UTC) + dt.timedelta(days=1),
        ip=None,
        is_admin=False,
    )


@pytest.fixture
def mock_expired_access_token_claim() -> AccessTokenClaim:
    return AccessTokenClaim(
        jti=uuid.uuid4(),
        sub="mock_sub",
        iat=dt.datetime.now(dt.UTC) - dt.timedelta(days=1),
        exp=dt.datetime.now(dt.UTC) - dt.timedelta(days=1),
        ip=None,
        is_admin=False,
    )


@pytest.fixture
def is_md5() -> Callable[[str], bool]:
    """
    Returns a function that checks if a string is a valid MD5 hash.

    Reference: https://stackoverflow.com/a/376889/19517403
    """

    def _is_md5(string: str) -> bool:
        matched = re.match(r"\b([a-f\d]{32}|[A-F\d]{32})\b", string)
        return bool(matched)

    return _is_md5


@pytest.fixture
def local_ip() -> IPvAnyAddress:
    return IPvAnyAddress("127.0.0.1")
