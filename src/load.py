import json
import re
from copy import deepcopy
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
    if schema is None:
        return obj

    parser = JsonSchemaParser(schema, extended_formats=extended_formats)
    return parser.parse(obj)


class JsonSchemaParser:

    def __init__(self, schema: Optional[dict] = None, extended_formats: Optional[dict] = None):
        self._extended_format = extended_formats
        self._orig_schema = schema

    def parse(self, obj):
        schema = deepcopy(self._orig_schema)
        return self._loado(obj, schema)

    def _loado(self, obj, schema: dict):
        """
        Like loads only handling an object instead of raw json.

        :param obj: the object to parse according to the schema
        :param schema: the schema to check according to
        """
        if '$ref' in schema:
            return self._resolve_refs(obj, schema['$ref'])

        return self._handle_composition(obj, schema)

    def _resolve_refs(self, obj, ref: str):
        if not isinstance(ref, str):
            raise ValueError('$ref has to be a string')

        if not ref.startswith('#'):
            raise ValueError(f'ref "{ref}" is not supported')

        path = ref.split('/')[1:]

        schema = self._orig_schema
        for key in path:
            schema = schema[key]

        return self._loado(obj, schema)

    def _handle_composition(self, obj, schema: dict):
        all_of = schema.pop('allOf', None)
        any_of = schema.pop('anyOf', None)
        one_of = schema.pop('oneOf', None)
        not_ = schema.pop('not', None)

        if not any((any_of, all_of, one_of, not_)):
            return self._handle_schema(obj, schema)

        ret = obj

        if not_ is not None:
            any_of_passed = False
            try:
                self._loado(obj, dict(**schema, **not_))
                any_of_passed = True
            except ValueError:
                pass

            if any_of_passed:
                raise ValueError('should not match the schema')

        if all_of is not None:
            for sub_schema in all_of[::-1]:
                ret = self._loado(obj, dict(**schema, **sub_schema))

        if any_of is not None:
            any_of_passed = False
            for sub_schema in any_of[::-1]:
                # noinspection PyBroadException
                try:
                    ret = self._loado(obj, dict(**schema, **sub_schema))
                    any_of_passed = True
                    break
                except Exception:
                    pass
            if not any_of_passed:
                raise ValueError('not passed any of the "anyOf" options')

        if one_of is not None:
            one_of_passed = 0
            for sub_schema in one_of[::-1]:
                try:
                    ret = self._loado(obj, dict(**schema, **sub_schema))
                    one_of_passed += 1
                except ValueError:
                    pass

            if one_of_passed != 1:
                raise ValueError('should apply only to one of the schemas')

        return ret

    def _handle_schema(self, obj, schema: dict):
        if 'const' in schema:
            if schema['const'] != obj:
                raise ValueError(f'value should be: {schema["const"]}')

            return obj

        match schema.get('type'):
            case None:
                return obj  # schema does not define a strict type, e.g. {"Title": "My Object"}

            case 'object':
                return self._object(obj, schema)

            case 'array':
                return self.validate_array(obj, schema)

            case 'string':
                return validate_string(obj, schema, extended_formats=self._extended_format)

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

    def _object(self, obj, schema: dict, **kwargs):
        # TODO: "unevaluatedProperties", "propertyNames"

        if not isinstance(obj, dict):
            raise ValueError('value is not a dict')

        self._validate_object_size(obj, schema)

        self._conditionals(obj, schema, **kwargs)

        ret = dict()

        properties_schema = schema.get('properties')
        pattern_properties = schema.get('patternProperties')
        remaining_keys = set(obj.keys())
        for key, value in dict(obj).items():
            if properties_schema is not None and key in properties_schema:
                ret[key] = self._loado(value, properties_schema[key])
                remaining_keys.remove(key)
                continue

            if pattern_properties is not None:
                for pattern, sub_schema in pattern_properties.items():
                    if re.search(pattern, key):
                        ret[key] = self._loado(value, sub_schema)
                        remaining_keys.remove(key)
                        break

        additional_properties = schema.get('additionalProperties')
        if additional_properties is False and len(remaining_keys) > 0:
            raise ValueError(f'additional properties are not allowed')
        elif isinstance(additional_properties, dict):
            for key in remaining_keys:
                ret[key] = self._loado(obj[key], additional_properties)
        else:
            ret.update(obj)

        return ret

    def _conditionals(self, obj, schema: dict, **kwargs):
        """
        Conditional are sets of validation options that do not affect the result objects type.
        """
        if 'required' in schema:
            for key in schema['required']:
                if key not in obj:
                    raise ValueError(f'filed "{key}" is required')

        if 'dependentRequired' in schema:
            for dependent, dependencies in schema['dependentRequired'].items():
                for dependency in dependencies:
                    if dependent in obj and dependency not in obj:
                        raise ValueError(f'"{dependent}" in dependent in "{dependency}"')

        # TODO: should work link allOf not in here
        if 'dependentSchemas' in schema:
            for dependent, dependency_schema in schema['dependentSchemas'].items():
                if dependent in obj:
                    self._loado(obj[dependent], dependency_schema)

        if 'if' in schema:
            try:
                self._loado(obj, schema['if'])
            except ValueError:
                if 'else' in schema:
                    self._loado(obj, schema['else'])
            else:
                if 'then' in schema:
                    self._loado(obj, schema['then'])

    @staticmethod
    def _validate_object_size(obj: dict, schema: dict):
        if 'minProperties' in schema and len(obj) < schema['minProperties']:
            raise ValueError(f'object should be longer then {schema["minProperties"]} items')

        if 'maxProperties' in schema and len(obj) > schema['maxProperties']:
            raise ValueError(f'object should be shorter then {schema["maxProperties"]} items')

    def validate_array(self, obj, schema: dict, **kwargs):
        if not isinstance(obj, list):
            raise ValueError('value is not an array')

        self._validate_array_range(obj, schema)

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
                    self._loado(item, contains_schema)
                    contains_count += 1
                except ValueError:
                    pass

            ret.append(self._handle_array_item(i, item, schema))

        if 'contains' in schema and \
                (contains_count < contains_min or (contains_max is not None and contains_count > contains_max)):
            raise ValueError('value does not comply with the "contains" rules')

        if schema.get('uniqueItems') is True and len(unique_check) != len(obj):
            raise ValueError('array values are not unique')

        return ret

    @staticmethod
    def _validate_array_range(obj: list, schema: dict):
        if 'minItems' in schema and len(obj) < schema['minItems']:
            raise ValueError('array length does not match "minItems"')

        if 'maxItems' in schema and len(obj) > schema['maxItems']:
            raise ValueError('array length does not match "maxItems"')

    def _handle_array_item(self, index: int, item, schema: dict, **kwargs):
        if 'prefixItems' in schema:
            if index < len(schema['prefixItems']):
                return self._loado(item, schema['prefixItems'][index])

            if schema.get('items') is False:
                raise ValueError('more items are not allowed')

        if 'items' in schema:
            return self._loado(item, schema['items'])

        return item
