import uuid
from datetime import time, datetime
from ipaddress import IPv4Address, IPv6Address

import pytest

from pyjschema import Formatter
from pyjschema.load import loads, JsonSchemaParser


def test_string():
    schema = {'type': 'string'}

    assert loads('"string"', schema) == 'string'
    assert loads('"21"', schema) == '21'

    with pytest.raises(ValueError):
        assert loads('{}', schema)

    with pytest.raises(ValueError):
        assert loads('[1,2]', schema)

    with pytest.raises(ValueError):
        assert loads("3", schema)


def test_uuid():
    schema = {'type': 'string', 'format': 'uuid'}

    assert isinstance(loads(f'"3e4666bf-d5e5-4aa7-b8ce-cefe41c7568a"', schema), uuid.UUID)

    schema = {'type': 'object', 'properties': {'uuid': {'type': 'string', 'format': 'uuid'}}}

    result = loads('{"uuid": "3e4666bf-d5e5-4aa7-b8ce-cefe41c7568a"}', schema)
    assert result == {'uuid': uuid.UUID('3e4666bf-d5e5-4aa7-b8ce-cefe41c7568a')}


def test_time():
    schema = {'type': 'string', 'format': 'time'}

    assert isinstance(loads(f'"20:20:39+00:00"', schema), time)


def test_duration():
    schema = {'type': 'string', 'format': 'duration'}

    assert loads(f'"P3DT12H"', schema) == timedelta(days=3, hours=12)


def test_datetime():
    schema = {'type': 'string', 'format': 'date-time'}

    assert isinstance(loads(f'"2018-11-13T20:20:39+00:00"', schema), datetime)


def test_ipv4():
    schema = {'type': 'string', 'format': 'ipv4'}

    assert isinstance(loads(f'"1.1.1.1"', schema), IPv4Address)
    with pytest.raises(ValueError):
        loads(f'"1.1.1.400"', schema)


def test_ipv6():
    schema = {'type': 'string', 'format': 'ipv6'}

    assert isinstance(loads(f'"2001:0000:130F:0000:0000:09C0:876A:130B"', schema), IPv6Address)
    with pytest.raises(ValueError):
        loads(f'"1.1.1.400"', schema)


def test_email():
    schema = {'type': 'string', 'format': 'email'}

    assert loads(f'"test12@gmail.com"', schema) == 'test12@gmail.com'
    with pytest.raises(ValueError):
        loads(f'"1.1.1.400"', schema)


# TODO: add all formats

def test_pattern():
    schema = {'type': 'string', 'pattern': '[a-z]*'}

    assert loads(f'"test"', schema) == 'test'
    with pytest.raises(ValueError):
        loads(f'"test1"', schema)


def test_length():
    schema = {'type': 'string', 'minLength': 3, 'maxLength': 5}

    assert loads(f'"test"', schema) == 'test'

    with pytest.raises(ValueError):
        loads(f'"t2"', schema)

    with pytest.raises(ValueError):
        loads(f'"t2sdfas"', schema)


def test_extended_formats():
    class BytesFormatter(Formatter):
        symbol = 'bytes'

        def decode(self, raw: str) -> bytes:
            return b64decode(raw)

        def encode(self, data: bytes) -> str:
            return b64encode(data).decode()

    schema = {'type': 'string', 'format': 'bytes'}
    parser = JsonSchemaParser(schema, extended_formats=[BytesFormatter])

    decoded = parser.loads('"SGVsbG8gV29ybGQh"')
    assert isinstance(decoded, bytes)
    assert decoded == b'Hello World!'
