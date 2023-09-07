from pyjschema.load import loads, _loado


def validate_raw(raw: bytes | str, schema: dict):
    loads(raw, schema)


def validate_obj(obj, schema: dict):
    _loado(obj, schema)
