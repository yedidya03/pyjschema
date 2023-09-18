import re
from typing import Type

from pyjschema.string.formatter import Formatter, UUIDFormat, DatetimeFormat, TimeFormat, DateFormat, EmailFormatter, \
    Ipv4Formatter, Ipv6Formatter, DurationFormatter, HostnameFormatter

DEFAULT_FORMATS: list[Type[Formatter]] = [
    UUIDFormat,
    DatetimeFormat,
    TimeFormat,
    DateFormat,
    DurationFormatter,
    EmailFormatter,
    Ipv4Formatter,
    Ipv6Formatter,
    HostnameFormatter,
]


def validate_string(obj, schema: dict, formats: dict[str, Formatter]):
    if not isinstance(obj, str):
        raise ValueError('value is not a string')

    _length(obj, schema)
    _pattern(obj, schema)

    f = schema.get('format')
    if f is None:
        return obj

    try:
        if f not in formats:
            raise ValueError(f'format {f} is not supported')

        return formats.get(f).decode(obj)

    except Exception as e:
        raise ValueError(f'error in formatting data, format: {schema["format"]}, error: {e}')


def _pattern(s: str, schema: dict):
    if 'pattern' in schema and not bool(re.fullmatch(schema['pattern'], s)):
        raise ValueError('value does not comply with the pattern')


def _length(s: str, schema: dict):
    if 'minLength' in schema and len(s) < schema['minLength']:
        raise ValueError(f"min length should be {schema['minLength']}, got {len(s)}")

    if 'maxLength' in schema and len(s) > schema['maxLength']:
        raise ValueError(f"max length should be {schema['maxLength']}, got {len(s)}")
