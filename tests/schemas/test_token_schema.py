import pytest

from app.core.security import encode_token
from app.schemas.token import AccessTokenClaim, TokenBase


def test_token_base_from_encoded(mock_access_token_claim: AccessTokenClaim):
    token = encode_token(mock_access_token_claim.model_dump())
    access_token_claim = AccessTokenClaim.from_encoded(token)
    assert access_token_claim.model_dump() == mock_access_token_claim.model_dump()

def test_token_base_from_encoded_validation_error():
    token = encode_token({"type": "invalid"})
    with pytest.raises(ValueError):
        TokenBase.from_encoded(token)

def test_token_base_from_encoded_allow_expired(mock_expired_access_token_claim: AccessTokenClaim):
    token = encode_token(mock_expired_access_token_claim.model_dump())
    access_token_claim = AccessTokenClaim.from_encoded(token, allow_expired=True)
    assert access_token_claim.model_dump() == mock_expired_access_token_claim.model_dump()

