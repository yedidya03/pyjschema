import pytest

from pyjschema.load import loads


def test_all_of():
    schema = {
        "allOf": [
            {"type": "string", 'minLength': 2},
            {'type': 'string', "maxLength": 5}
        ]
    }

    loads('"good"', schema)

    with pytest.raises(ValueError):
        loads('"too long"', schema)

    with pytest.raises(ValueError):
        loads('"1"', schema)


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


def test_with_conditionals():
    schema = {
        "type": "object",
        "properties": {
            "street_address": {
                "type": "string"
            },
            "country": {
                "default": "United States of America",
                "enum": ["United States of America", "Canada", "Netherlands"]
            }
        },
        "allOf": [
            {
                "if": {
                    'type': 'object',
                    "properties": {"country": {"const": "United States of America"}}
                },
                "then": {
                    "type": "object", "properties": {
                        "postal_code": {'type': 'string', "pattern": "[0-9]{5}(-[0-9]{4})?"}
                    }
                }
            },
            {
                "if": {
                    "type": "object",
                    "properties": {"country": {"const": "Canada"}},
                    "required": ["country"]
                },
                "then": {
                    "type": "object",
                    "properties": {"postal_code": {'type': 'string', "pattern": "[A-Z][0-9][A-Z] [0-9][A-Z][0-9]"}}
                }
            },
            {
                "if": {
                    "type": "object",
                    "properties": {"country": {"const": "Netherlands"}},
                    "required": ["country"]
                },
                "then": {
                    "type": "object",
                    "properties": {"postal_code": {'type': 'string', "pattern": "[0-9]{4} [A-Z]{2}"}}
                }
            }
        ]
    }

    loads('''{
      "street_address": "1600 Pennsylvania Avenue NW",
      "country": "United States of America",
      "postal_code": "20500"
    }''', schema)

    loads('''{
      "street_address": "1600 Pennsylvania Avenue NW",
      "postal_code": "20500"
    }''', schema)

    loads('''{
      "street_address": "24 Sussex Drive",
      "country": "Canada",
      "postal_code": "K1M 1M4"
    }''', schema)

    loads('''{
      "street_address": "Adriaan Goekooplaan",
      "country": "Netherlands",
      "postal_code": "2517 JX"
    }''', schema)

    with pytest.raises(ValueError):
        loads('''{
          "street_address": "24 Sussex Drive",
          "country": "Canada",
          "postal_code": "10000"
        }''', schema)

    with pytest.raises(ValueError):
        loads('''{
          "street_address": "1600 Pennsylvania Avenue NW",
          "postal_code": "K1M 1M4"
        }''', schema)
