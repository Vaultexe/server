import pytest

from app.schemas.user import UserInvite, UserResetPassword


def test_user_invite_auto_pass():
    invite = UserInvite(
        email="test@example.com",
        is_admin=False,
    )
    assert invite.master_pwd_hash is not None


def test_user_reset_pwd_auto_pass():
    user_reset_pwd_obj = UserResetPassword(
        curr_pwd_hash="sample_hash",
        new_pwd_hash="sample_hash2",
    )
    assert isinstance(user_reset_pwd_obj, UserResetPassword)


def test_user_reset_pwd_same_pwd_error():
    with pytest.raises(ValueError):
        UserResetPassword(
            curr_pwd_hash="sample_hash",
            new_pwd_hash="sample_hash",
        )
