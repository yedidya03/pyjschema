

def validate_number(obj, schema: dict):
    if not (isinstance(obj, float) or isinstance(obj, int)):
        raise ValueError('value is not a number')

    if 'minimum' in schema and obj < schema['minimum']:
        raise ValueError(f'value is less then {schema["minimum"]}')

    if 'exclusiveMinimum' in schema and obj <= schema['exclusiveMinimum']:
        raise ValueError(f'value is less or equal then {schema["exclusiveMinimum"]}')

    if 'maximum' in schema and obj > schema['maximum']:
        raise ValueError(f'value is more then {schema["maximum"]}')

    if 'exclusiveMaximum' in schema and obj >= schema['exclusiveMaximum']:
        raise ValueError(f'value is more or equal then {schema["exclusiveMaximum"]}')

    if 'multipleOf' in schema and not (obj / schema['multipleOf']).is_integer():
        raise ValueError(f'value is not a multiply {schema["multipleOf"]}')

    return obj
