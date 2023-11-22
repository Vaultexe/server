from app.core import security
from app.models.user import User


def test_update_password() -> None:
    user = User()
    master_key_hash = "mock_pwd"
    user.update_password(master_key_hash)
    assert security.verify_pwd(master_key_hash, user.master_pwd_hash)


def test_activate() -> None:
    user = User()
    user.activate()
    assert user.is_active is True


def test_verify_email() -> None:
    user = User()
    user.verify_email()
    assert user.email_verified is True
