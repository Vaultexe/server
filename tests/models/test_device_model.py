import datetime as dt
import uuid

from pydantic import IPvAnyAddress

from app.models import Device
from app.schemas import DeviceCreate


def test_refresh_last_login(local_ip: IPvAnyAddress) -> None:
    device = Device()
    device.refresh_last_login(local_ip)
    assert device.last_login_ip == str(local_ip)
    assert isinstance(device.last_login_at, dt.datetime)


def test_verify() -> None:
    device = Device()
    device.verify()
    assert device.is_verified is True


def test_import_from(local_ip) -> None:
    device_create = DeviceCreate(
        ip=local_ip,
        is_verified=True,
        user_agent="mock_user_agent",
        user_id=uuid.uuid4(),
    )
    device = Device()
    device.import_from(device_create)

    assert device.user_id == device_create.user_id
    assert device.is_verified == device_create.is_verified
    assert device.user_agent == device_create.user_agent
    assert device.last_login_ip == str(local_ip)
    assert isinstance(device.last_login_at, dt.datetime)
    assert getattr(device, "ip", None) is None
