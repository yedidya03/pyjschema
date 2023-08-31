import base64
import json
import uuid
from datetime import datetime
from typing import Optional, Callable, Any


def loads(raw: str | bytes, schema: Optional[dict] = None):
    """
    Like json.loads(), only that if a schema is given, it validates the data according to the schema and fills the
    fields in pythonic types according to the schema (for example datetime for type "string" and forma "date-time").

    For more information about json schema see: https://json-schema.org/understanding-json-schema

    :param raw: the json to parse according to the schema
    :param schema: the schema to check according to

    TODO: add the params options of json.loads to this function
    """
    obj = json.loads(raw)
    return loado(obj, schema)


# TODO: complete formats
DEFAULT_FORMATS: dict[str, Callable[[str], Any]] = {
    'uuid': uuid.UUID.__init__,
    'date-time': datetime.fromisoformat,
    'time': datetime.fromisoformat,
    'date': datetime.fromisoformat,
    'duration': lambda x: x,
    'bytes': base64.b64decode
}


def loado(obj, schema: Optional[dict] = None, extended_formats: Optional[dict] = None):
    """
    Like loads only handling an object instead of raw json.

    :param obj: the object to parse according to the schema
    :param schema: the schema to check according to
    :param extended_formats: more formats for string parsing
    """
    if schema is None:
        return obj

    match schema['type']:
        case 'object':
            return _object(obj, schema, extended_formats=extended_formats)

        case 'array':
            return _array(obj, schema, extended_formats=extended_formats)

        case 'string':
            return _string(obj, schema, extended_formats)

        case 'number' | 'integer':
            # TODO: "multipleOf", "minimum", "exclusiveMinimum", "maximum", "exclusiveMaximum"

            if not (isinstance(obj, float) or isinstance(obj, int)):
                raise ValueError('value is not a number')

        case 'boolean':
            if not isinstance(obj, bool):
                raise ValueError('value is not a boolean')

        case 'null':
            if obj is not None:
                raise ValueError('value is not null')

        case _:
            raise ValueError(f'type {schema["type"]} is not supported')

    return obj


def _object(obj, schema: Optional[dict] = None, **kwargs):
    # TODO: "patternProperties", "unevaluatedProperties", "propertyNames", "minProperties", "maxProperties"

    if not isinstance(obj, dict):
        raise ValueError('value is not a dict')

    if 'properties' not in schema:
        return obj

    ret, required = dict(), set()
    if 'required' in schema:
        required = set(schema['required'])

    for prop, prop_schema in schema['properties'].items():
        if prop in obj:
            ret[prop] = loado(obj.pop(prop), prop_schema, **kwargs)

        elif prop in required:
            raise ValueError(f'filed "{prop}" is required')

    if 'additionalProperties' in schema and len(obj) > 0:
        raise ValueError(f'additional properties are not allowed')
    else:
        ret.update(obj)

    return ret


def _array(obj, schema: Optional[dict] = None, **kwargs):
    # TODO: "prefixItems", "contains", "minItems", "maxItems", "uniqueItems"

    if not isinstance(obj, list):
        raise ValueError('value is not an array')

    ret = []

    if 'items' in schema:
        for item in obj:
            ret.append(loado(item, schema['items'], **kwargs))

    return ret


def _string(obj, schema: Optional[dict] = None, extended_formats: Optional[dict] = None):
    # TODO: "pattern", more formats

    if not isinstance(obj, str):
        raise ValueError('value is not a string')

    f = schema.get('format')
    if f is None:
        return obj

    try:
        if f not in DEFAULT_FORMATS and (extended_formats is None or f not in extended_formats):
            raise ValueError(f'format {f} is not supported')

        formatter = DEFAULT_FORMATS.get(f)
        if formatter is None:
            formatter = extended_formats[f]

        return formatter(obj)

    except Exception as e:
        raise ValueError(f'error in formatting data, format: {schema["format"]}, error: {e}')
