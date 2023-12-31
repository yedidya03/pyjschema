import pytest

from pyjschema.load import loads


def test_properties():
    schema = {
        'type': 'object',
        'properties': {
            'number': {'type': 'number'},
            'array': {'type': 'array', 'items': {'type': 'string'}}
        }
    }

    loads('{"number": 12.3}', schema)
    with pytest.raises(ValueError):
        loads('{"number": "12.3"}', schema)

    loads('{"number": 12.3, "array": []}', schema)
    loads('{"number": 12.3, "array": ["a", "b"]}', schema)
    with pytest.raises(ValueError):
        loads('{"number": 12.3, "array": ["a", 2]}', schema)


def test_pattern_properties():
    schema = {
        "type": "object",
        "patternProperties": {
            "^S_": {"type": "string"},
            "^I_": {"type": "integer"}
        }
    }

    loads('{ "S_25": "This is a string" }', schema)
    loads('{ "I_0": 42 }', schema)
    loads('{ "keyword": "value" }', schema)
    with pytest.raises(ValueError):
        loads('{ "S_0": 42 }', schema)

    with pytest.raises(ValueError):
        loads('{ "I_42": "This is a string" }', schema)


def test_properties_and_pattern_properties():
    schema = {
        "type": "object",
        "patternProperties": {
            "^S_": {"type": "string"},
            "^I_": {"type": "integer"}
        },
        'properties': {
            'number': {'type': 'number'},
            'array': {'type': 'array', 'items': {'type': 'string'}}
        }
    }

    loads('{ "S_25": "This is a string" }', schema)
    loads('{ "I_0": 42 }', schema)
    loads('{ "keyword": "value" }', schema)
    with pytest.raises(ValueError):
        loads('{ "S_0": 42 }', schema)

    with pytest.raises(ValueError):
        loads('{ "I_42": "This is a string" }', schema)

    loads('{"number": 12.3}', schema)
    with pytest.raises(ValueError):
        loads('{"number": "12.3"}', schema)

    loads('{"number": 12.3, "array": []}', schema)
    loads('{"number": 12.3, "array": ["a", "b"]}', schema)
    with pytest.raises(ValueError):
        loads('{"number": 12.3, "array": ["a", 2]}', schema)

    loads('{"number": 12.3, "array": [], "I_0": 42, "another": 1}', schema)
    with pytest.raises(ValueError):
        loads('{"S_0": 42, "number": 12.3}', schema)

    with pytest.raises(ValueError):
        loads('{"array": [], "number": "12"}', schema)


def test_no_additional_properties():
    schema = {
        'type': 'object',
        'required': ['a1'],
        'properties': {
            'a1': {'type': 'number'},
            'a2': {'type': 'array', 'items': {'type': 'string'}}
        },
        'additionalProperties': False
    }

    loads('{"a1": 12.3, "a2": ["213"]}', schema)
    loads('{"a1": 12.3}', schema)
    with pytest.raises(ValueError):
        loads('{"a1": "12.3", "additional": 12}', schema)


def test_additional_properties_schema():
    schema = {
        "type": "object",
        "properties": {
            "number": {"type": "number"},
            "street_name": {"type": "string"},
        },
        "additionalProperties": {"type": "string"}
    }

    loads('{"number": 1600, "street_name": "Pennsylvania"}', schema)
    loads('{"number": 1600, "street_name": "Pennsylvania", "additional": "NW"}', schema)
    with pytest.raises(ValueError):
        loads('{"number": 1600, "street_name": "Pennsylvania", "additional": 201}', schema)


def test_additional_properties_combined():
    schema = {
        "type": "object",
        "properties": {
            "builtin": {"type": "number"}
        },
        "patternProperties": {
            "^S_": {"type": "string"},
            "^I_": {"type": "integer"}
        },
        "additionalProperties": {"type": "string"}
    }

    loads('{"builtin": 42}', schema)
    loads('{"keyword": "value"}', schema)
    with pytest.raises(ValueError):
        loads('{"keyword": 42}', schema)


def test_required():
    schema = {'type': 'object', 'required': ['a1', 'a2']}

    loads('{"a1": 12.3, "a2": "213"}', schema)
    loads('{"a1": 12.3, "a2": "213", "a3": "123123"}', schema)
    with pytest.raises(ValueError):
        loads('{"a1": "12.3"}', schema)

    with pytest.raises(ValueError):
        loads('{"a2": "12.3"}', schema)


def test_dependent_required():
    schema = {
        'type': "object",
        "properties": {
            "name": {"type": "string"},
            "credit_card": {"type": "number"},
            "billing_address": {"type": "string"}
        },
        "required": ["name"],
        "dependentRequired": {
            "credit_card": ["billing_address"]
        }
    }

    loads('''{"name": "John Doe", "credit_card": 5555555555555555, "billing_address": "555 Debtor's Lane"}''', schema)
    loads('''{"name": "John Doe"}''', schema)
    loads('''{"name": "John Doe", "billing_address": "555 Debtor's Lane"}''', schema)

    with pytest.raises(ValueError):
        loads('''{"name": "John Doe", "credit_card": 5555555555555555}''', schema)

    schema = {
        'type': "object",
        "properties": {
            "name": {"type": "string"},
            "credit_card": {"type": "number"},
            "billing_address": {"type": "string"}
        },
        "required": ["name"],
        "dependentRequired": {
            "credit_card": ["billing_address"],
            "billing_address": ["credit_card"]
        }
    }

    with pytest.raises(ValueError):
        loads('''{"name": "John Doe", "credit_card": 5555555555555555}''', schema)

    with pytest.raises(ValueError):
        loads('''{"name": "John Doe", "billing_address": "555 Debtor's Lane"}''', schema)


def test_object_size():
    schema = {'type': 'object', 'minProperties': 2, 'maxProperties': 3}

    loads('{"a1": 12.3, "a2": "213"}', schema)
    loads('{"a1": 12.3, "a2": "213", "a3": "123123"}', schema)

    with pytest.raises(ValueError):
        loads('{}', schema)

    with pytest.raises(ValueError):
        loads('{"1": 1}', schema)

    with pytest.raises(ValueError):
        loads('{"a1": 1, "a2": "12.3", "a3": 4, "a4": 1}', schema)


def test_if_then_else():
    schema = {
        "type": "object",
        "properties": {
            "street_address": {
                "type": "string"
            },
            "country": {
                "default": "United States of America",
                "enum": ["United States of America", "Canada"]
            }
        },
        "if": {
            "type": "object", "properties": {"country": {"const": "United States of America"}}
        },
        "then": {
            "type": "object", "properties": {"postal_code": {'type': 'string', "pattern": "[0-9]{5}(-[0-9]{4})?"}}
        },
        "else": {
            "type": "object", "properties": {
                "postal_code": {'type': 'string', "pattern": "[A-Z][0-9][A-Z] [0-9][A-Z][0-9]"}
            }
        }
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
