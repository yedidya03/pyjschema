from src.load import loads


def test_refs():
    schema = {
        "$id": "https://example.com/schemas/customer",

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

