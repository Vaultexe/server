import datetime as dt
import json
from typing import Any

from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

"""
Heavily inspired by fastapi-cache
https://github.com/long2ice/fastapi-cache/blob/ee58f979d4ef22a03012d86efb6fdb7b5f5b91c6/fastapi_cache/coder.py#L53
"""

TYPE_CONVERTER = {
    "datetime": lambda x: dt.datetime.fromisoformat(x),
    "date": lambda x: dt.date.fromisoformat(x),
}


class JsonEncoder(json.JSONEncoder):
    """
    Custom JSON encoder to handle custom types over JSON.
    """

    def default(self, obj: Any) -> Any:
        """
        Override json.JSONEncoder.default method to handle custom types.
        Convert certain custom types to their JSON representation.
        """
        if isinstance(obj, dt.datetime):
            return {"__type__": "datetime", "val": obj.isoformat()}
        elif isinstance(obj, dt.date):
            return {"__type__": "date", "val": obj.isoformat()}
        return jsonable_encoder(obj)


def object_hook(obj: dict) -> Any:
    """
    Convert certain custom encoded types to their original form.
    """
    type = obj.get("__type__", None)

    if type is None:
        return obj

    if type not in TYPE_CONVERTER:
        raise TypeError(f"Type {type} not supported")

    return TYPE_CONVERTER[type](obj["val"])


class JsonCoder:
    """
    Json coder for encoding and decoding values.
    Uses custom JSON encoder & object hook decoder
    """

    @classmethod
    def encode(cls, value: Any) -> bytes:
        if isinstance(value, JSONResponse):
            return value.body
        return json.dumps(value, cls=JsonEncoder).encode()

    @classmethod
    def decode(cls, value: bytes) -> Any:
        return json.loads(value, object_hook=object_hook)
