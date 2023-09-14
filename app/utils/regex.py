import re


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
