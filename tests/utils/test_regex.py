import pytest

from app.utils.regex import camel_to_snake


@pytest.mark.parametrize('input, expected', [
    ('', ''),
    ('HTTP', 'http'),
    ('CamelCase', 'camel_case'),
    ('camel_camel_case', 'camel_camel_case'),
    ('HTTPResponseCode', 'http_response_code'),
    ('HTTPResponseCodeXYZ', 'http_response_code_xyz'),
])
def test_camel_to_snake(input: str, expected: str):
    assert camel_to_snake(input) == expected
