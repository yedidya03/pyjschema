import uuid
from datetime import time, datetime

import pytest

from src.load import loads


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


def test_time():
    schema = {'type': 'string', 'format': 'time'}

    assert isinstance(loads(f'"20:20:39+00:00"', schema), time)


def test_datetime():
    schema = {'type': 'string', 'format': 'date-time'}

    assert isinstance(loads(f'"2018-11-13T20:20:39+00:00"', schema), datetime)


def test_ipv4():
    schema = {'type': 'string', 'format': 'ipv4'}

    loads(f'"1.1.1.1"', schema)
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
