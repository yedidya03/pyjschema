import json
from typing import Optional

from src.number import validate_number
from src.string import validate_string


def loads(raw: str | bytes, schema: Optional[dict] = None, extended_formats: Optional[dict] = None, **kwargs):
    """
    Like json.loads(), only that if a schema is given, it validates the data according to the schema and fills the
    fields in pythonic types according to the schema (for example datetime for type "string" and forma "date-time").

    For more information about json schema see: https://json-schema.org/understanding-json-schema

    :param raw: the json to parse according to the schema
    :param schema: the schema to check according to
    :param extended_formats: more formats for string parsing

    TODO: add the params options of json.loads to this function
    """
    obj = json.loads(raw, **kwargs)
    return loado(obj, schema, extended_formats=extended_formats)


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
            return validate_array(obj, schema, extended_formats=extended_formats)

        case 'string':
            return validate_string(obj, schema, extended_formats)

        case 'number' | 'integer':
            return validate_number(obj, schema)

        case 'boolean':
            if not isinstance(obj, bool):
                raise ValueError('value is not a boolean')

        case 'null':
            if obj is not None:
                raise ValueError('value is not null')

        case _:
            raise ValueError(f'type {schema["type"]} is not supported')

    return obj


def _object(obj, schema: dict, **kwargs):
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


def validate_array(obj, schema: dict, **kwargs):
    if not isinstance(obj, list):
        raise ValueError('value is not an array')

    _validate_array_range(obj, schema)

    contains_count, contains_schema, contains_min, contains_max = 0, None, None, None
    if 'contains' in schema:
        contains_schema = schema['contains']
        contains_min = schema.get('minContains', 1)
        contains_max = schema.get('maxContains', None)

    ret, unique_check = [], set()
    for i, item in enumerate(obj):
        if schema.get('uniqueItems') is True:
            unique_check.add(item)

        if 'contains' in schema:
            try:
                loado(item, contains_schema, **kwargs)
                contains_count += 1
            except ValueError:
                pass

        ret.append(_handle_array_item(i, item, schema, **kwargs))

    if 'contains' in schema and (contains_count < contains_min or (contains_max is not None and contains_count > contains_max)):
        raise ValueError('value does not comply with the "contains" rules')

    if schema.get('uniqueItems') is True and len(unique_check) != len(obj):
        raise ValueError('array values are not unique')

    return ret


def _validate_array_range(obj: list, schema: dict):
    if 'minItems' in schema and len(obj) < schema['minItems']:
        raise ValueError('array length does not match "minItems"')

    if 'maxItems' in schema and len(obj) > schema['maxItems']:
        raise ValueError('array length does not match "maxItems"')


def _handle_array_item(index: int, item, schema: dict, **kwargs):
    if 'prefixItems' in schema:
        if index < len(schema['prefixItems']):
            return loado(item, schema['prefixItems'][index], **kwargs)

        if schema.get('items') is False:
            raise ValueError('more items are not allowed')

    if 'items' in schema:
        return loado(item, schema['items'], **kwargs)

    return item
