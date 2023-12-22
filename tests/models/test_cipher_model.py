import datetime as dt
import uuid

from app.models.cipher import Cipher
from app.schemas.cipher import CipherCreate
from app.schemas.enums import CipherType


def test_cipher_import_from() -> None:
    obj = CipherCreate(type=CipherType.LOGIN, data=b"test", collection_id=uuid.uuid4())
    cipher = Cipher()
    cipher.import_from(obj)
    assert cipher.type == obj.type
    assert cipher.data == obj.data
    assert cipher.collection_id == obj.collection_id


def test_cipher_import_from_exclude_unset() -> None:
    obj = CipherCreate(
        type=CipherType.LOGIN,
        data=b"test",
    )
    cipher = Cipher()
    cipher.import_from(obj)
    assert cipher.type == obj.type
    assert cipher.data == obj.data
    assert cipher.collection_id is None


def test_cipher_spft_delete() -> None:
    cipher = Cipher()
    cipher.soft_delete()
    assert isinstance(cipher.deleted_at, dt.datetime)
