import pytest

from pyjschema.load import loads


def test_refs():
    schema = {
        "type": "object",
        "properties": {
            "first_name": {"$ref": "#/$defs/name"},
            "last_name": {"$ref": "#/$defs/name"},
        },
        "required": ["first_name", "last_name"],

        "$defs": {
            "name": {"type": "string"}
        }
    }

    loads('{"first_name": "safd", "last_name": "asdf"}', schema)


def test_recursion():
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "children": {
                "type": "array",
                "items": {"$ref": "#"}
            }
        }
    }

    loads('''
    {
      "name": "Elizabeth",
      "children": [
        {"name": "Charles", "children": [
            {"name": "William", "children": [{ "name": "George" }, { "name": "Charlotte" }]},
            {"name": "Harry"}
        ]}
      ]
    }
    ''', schema)

    with pytest.raises(ValueError):
        loads('''
        {
          "name": "Elizabeth",
          "children": [
            {"name": "Charles", "children": [
                {"name": "William", "children": [{"name": 1}, {"name": "Charlotte"}]},
                {"name": "Harry"}
            ]}
          ]
        }
        ''', schema)
