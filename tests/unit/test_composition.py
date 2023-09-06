import pytest

from src.load import loads


def test_all_of():
    schema = {
        "allOf": [
            {"type": "string"},
            {"maxLength": 5}
        ]
    }

    loads('"short"', schema)
    with pytest.raises(ValueError):
        loads('"too long"', schema)


def test_any_of():
    schema = {
        "anyOf": [
            {"type": "string", "maxLength": 5},
            {"type": "number", "minimum": 0}
        ]
    }

    loads('"short"', schema)
    loads('12', schema)

    with pytest.raises(ValueError):
        loads('-5', schema)

    with pytest.raises(ValueError):
        loads('"too long"', schema)


def test_one_of():
    schema = {
        "oneOf": [
            {"type": "number", "multipleOf": 5},
            {"type": "number", "multipleOf": 3}
        ]
    }

    loads('10', schema)
    loads('9', schema)

    with pytest.raises(ValueError):
        loads('2', schema)

    with pytest.raises(ValueError):
        loads('15', schema)


def test_not():
    schema = {'not': {'type': 'string'}}

    loads('10', schema)
    loads('{ "key": "value" }', schema)

    with pytest.raises(ValueError):
        loads('"I am a string"', schema)


def test_factories():
    schema = {
        'type': 'number',
        "oneOf": [
            {"multipleOf": 5},
            {"multipleOf": 3}
        ]
    }

    loads('10', schema)
    loads('6', schema)

    with pytest.raises(ValueError):
        loads('"I am a string"', schema)

    with pytest.raises(ValueError):
        loads('4', schema)
