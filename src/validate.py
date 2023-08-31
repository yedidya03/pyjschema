from src.load import loads, loado


def validate_raw(raw: bytes | str, schema: dict):
    loads(raw, schema)


def validate_obj(obj, schema: dict):
    loado(obj, schema)
