import datetime as dt
import uuid

import pytest

from app.schemas.invitation import InvitationCreate


@pytest.fixture
def invitation():
    return InvitationCreate(
        token=uuid.uuid4(),
        invitee_id=uuid.uuid4(),
        created_by=uuid.uuid4(),
        created_at=dt.datetime.now(),
        expires_at=dt.datetime.now(),
    )

def test_invitation_create_token_hash(invitation:InvitationCreate):
    assert invitation.token_hash is not None

def test_invitation_create_dumps(invitation:InvitationCreate):
    dump = invitation.model_dump()
    assert "token" not in dump
