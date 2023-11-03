import pytest

from app.utils.regex import camel_to_snake, generate_password, is_valid_password


@pytest.mark.parametrize(
    "input, expected",
    [
        ("", ""),
        ("HTTP", "http"),
        ("CamelCase", "camel_case"),
        ("camel_camel_case", "camel_camel_case"),
        ("HTTPResponseCode", "http_response_code"),
        ("HTTPResponseCodeXYZ", "http_response_code_xyz"),
    ],
)
def test_camel_to_snake(input: str, expected: str):
    assert camel_to_snake(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    [
        ("", False),
        ("12345678", False),
        ("password", False),
        ("Password", False),
        ("Password123", False),
        ("!@#$%^&*()_+-", False),
        ("Password123!", True),
        ("Password123[", True),
        ("Aa1!@#$%^&*()_+-", True),
    ],
)
def test_is_valid_password(input: str, expected: bool):
    assert is_valid_password(input) == expected


@pytest.mark.parametrize("input, expected", [(generate_password(), True) for _ in range(100)])
def test_generate_password(input: str, expected: bool):
    assert is_valid_password(input) == expected
