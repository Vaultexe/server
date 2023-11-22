import datetime as dt
import uuid

from app.models.invitation import Invitation
from app.schemas import InvitationCreate


def test_invitation_create_from():
    # Arrange
    obj = InvitationCreate(
        token=uuid.uuid4(),
        invitee_id=uuid.uuid4(),
        created_by=uuid.uuid4(),
        expires_at=dt.datetime.now(dt.UTC) + dt.timedelta(days=1),
    )

    # Act
    invitation = Invitation.create_from(obj)

    # Assert
    assert invitation.token_hash == obj.token_hash
    assert invitation.invitee_id == obj.invitee_id
    assert invitation.created_by == obj.created_by
    assert invitation.expires_at == obj.expires_at
    assert invitation.is_expired is False


def test_invitation_is_expired():
    # Arrange
    obj = InvitationCreate(
        token=uuid.uuid4(),
        invitee_id=uuid.uuid4(),
        created_by=uuid.uuid4(),
        expires_at=dt.datetime.now(dt.UTC) + dt.timedelta(days=1),
    )
    expired_obj = obj.model_copy(update={"expires_at": dt.datetime.now(dt.UTC) - dt.timedelta(days=1)})

    # Act
    invitation = Invitation.create_from(obj)
    expired_invitation = Invitation.create_from(expired_obj)

    # Assert
    assert invitation.is_expired is False
    assert expired_invitation.is_expired is True

