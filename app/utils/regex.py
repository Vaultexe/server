import re
import secrets
import string
import uuid


def camel_to_snake(text: str) -> str:
    """
    Converts CamelCase to snake_case

    Usage:
        >>> camel_to_snake('HTTPResponseCodeXYZ')
        'http_response_code_xyz'
        >>> camel_to_snake('getHTTPResponseCode')
        'get_http_response_code'
    """
    # https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
    expression = r"((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))"
    replacement_exp = r"_\1"
    return re.sub(expression, replacement_exp, text).lower()


_rpunctuation = string.punctuation + "\\\\"
rchars = string.ascii_letters + string.digits + _rpunctuation + " "


def generate_password(min_length: int = 16) -> str:
    """
    Generates a random password.

    Args:
        min_length: minimum length of password (default: 16)

    Constraints:
        At least 8 characters long
        At least 1 uppercase letter
        At least 1 lowercase letter
        At least 1 digit
        At least 1 special character

    Usage:
        >>> generate_password()
        'wq5Y0!h6#X3@9^E7'
        >>> generate_password(8)
        '9^E7wq5Y'
    """
    if min_length < 8:
        raise ValueError("Minimum length of password should be at least 8 characters.")

    c1 = secrets.choice(string.ascii_lowercase)
    c2 = secrets.choice(string.ascii_uppercase)
    c3 = secrets.choice(string.digits)
    c4 = secrets.choice(string.punctuation)

    password = "".join(secrets.choice(rchars) for _ in range(min_length - 4))
    return password + c1 + c2 + c3 + c4


def is_valid_password(password: str) -> bool:
    """
    Checks if password is valid.

    Valid password:
        - At least 8 characters long
        - At least 1 uppercase letter
        - At least 1 lowercase letter
        - At least 1 digit
        - At least 1 special character

    Usage:
        >>> is_valid_password('Password123!')
        True
        >>> is_valid_password('password123!')
        False

    References:
        - https://stackoverflow.com/questions/19605150/regex-for-password-must-contain-at-least-eight-characters-at-least-one-number-a

    """
    expression = (
        rf"^(?=.*[{string.ascii_uppercase}])"  # At least 1 uppercase letter
        rf"(?=.*[{string.ascii_lowercase}])"  # At least 1 lowercase letter
        rf"(?=.*[{string.digits}])"  # At least 1 digit
        rf"(?=.*[{_rpunctuation}])"  # At least 1 special character
        f"[{rchars}]"
        r"{8,}$"  # At least 8 characters long
    )
    match = re.match(expression, password)
    return bool(match)


def uuid4_str() -> str:
    """Generates a string uuid4"""
    return str(uuid.uuid4())
