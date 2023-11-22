import pytest

from app.utils.regex import (
    camel_to_snake,
    capitalize_first_letter,
    generate_password,
    is_valid_password,
    uuid4_str,
)


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


def test_generate_password():
    for _ in range(100):
        input = generate_password()
        assert is_valid_password(input)


def test_generate_password_length_error():
    with pytest.raises(ValueError):
        generate_password(7)


def test_uuid4_str():
    assert isinstance(uuid4_str(), str)


@pytest.mark.parametrize(
    "input, expected",
    [
        ("", ""),
        ("a", "A"),
        ("hello", "Hello"),
        ("world", "World"),
        ("github copilot", "Github copilot"),
        ("test", "Test"),
    ],
)
def test_capitalize_first_letter(input: str, expected: str):
    assert capitalize_first_letter(input) == expected
