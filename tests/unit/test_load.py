import pytest

from pyjschema.load import loads


def test_bool():
    pass


def test_null():
    pass


def test_array():
    pass


def test_loads():
    schema = {
        "type": "object",
        "properties": {
            'number': {
                'type': 'number'
            },
            'array': {
                'type': 'array',
                'items': {
                    'type': 'string'
                }
            }
        }
    }

    loads('{"number": 12.3}', schema)
    with pytest.raises(ValueError):
        loads('{"number": "12.3"}', schema)

    loads('{"number": 12.3, "array": []}', schema)
    loads('{"number": 12.3, "array": ["a", "b"]}', schema)
    with pytest.raises(ValueError):
        loads('{"number": 12.3, "array": ["a", 2]}', schema)


def test_const():
    schema = {
        'type': 'object',
        "properties": {
            "country": {
                "const": "United States of America"
            }
        }
    }

    loads('{ "country": "United States of America" }', schema)
    with pytest.raises(ValueError):
        loads('{ "country": "Canada" }', schema)
