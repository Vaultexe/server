import datetime as dt
import json

import pytest
from starlette.responses import JSONResponse

from app.utils.coders import JsonCoder, JsonEncoder, object_hook


def test_json_encoder():
    encoder = JsonEncoder()
    datetime_obj = dt.datetime.now()
    date_obj = dt.date.today()
    random_obj = {"key": "value"}

    # Test encoding datetime object
    encoded_datetime = encoder.default(datetime_obj)
    assert encoded_datetime["__type__"] == "datetime"
    assert encoded_datetime["val"] == datetime_obj.isoformat()

    # Test encoding date object
    encoded_date = encoder.default(date_obj)
    assert encoded_date["__type__"] == "date"
    assert encoded_date["val"] == date_obj.isoformat()

    # Test encoding random object
    encoded_random = encoder.default(random_obj)
    assert encoded_random == random_obj

def test_object_hook():
    datetime_obj = dt.datetime.now()
    date_obj = dt.date.today()

    # Test decoding datetime object
    decoded_datetime = object_hook({"__type__": "datetime", "val": datetime_obj.isoformat()})
    assert decoded_datetime == datetime_obj

    # Test decoding date object
    decoded_date = object_hook({"__type__": "date", "val": date_obj.isoformat()})
    assert decoded_date == date_obj

    # Test decoding random object
    decoded_random = object_hook({"key": "value"})
    assert decoded_random == {"key": "value"}


def test_object_hook_type_error():
    with pytest.raises(TypeError):
        object_hook({"__type__": "random_type", "val": "random_val"})


def test_json_coder():
    datetime_obj = dt.datetime.now()
    date_obj = dt.date.today()
    json_response = JSONResponse({"key":"value"})

    # Test encoding and decoding datetime object
    encoded_datetime = JsonCoder.encode(datetime_obj)
    decoded_datetime = JsonCoder.decode(encoded_datetime)
    assert decoded_datetime == datetime_obj

    # Test encoding and decoding date object
    encoded_date = JsonCoder.encode(date_obj)
    decoded_date = JsonCoder.decode(encoded_date)
    assert decoded_date == date_obj

    # Test encoding and decoding a JSONResponse object
    encoded_json_response: bytes = JsonCoder.encode(json_response)
    decoded_json_response: dict = JsonCoder.decode(encoded_json_response)
    assert decoded_json_response == json.loads(json_response.body)
