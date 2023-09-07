import base64
import ipaddress
import re
import uuid
from datetime import datetime, time, timedelta
from typing import Callable, Any, Optional

from fqdn import FQDN


def _email(s: str) -> str:
    if '@' not in s:
        raise ValueError('email not valid')

    return s


date_signs = {'Y': 'years', 'M': 'months', 'W': 'weeks', 'D': 'days'}
time_signs = {'H': 'hours', 'M': 'minutes', 'S': 'seconds'}


def _build_duration(s: str, signs: dict[str, str]) -> timedelta:
    build = {}
    last = 0
    for i, c in enumerate(s):
        if c in signs:
            build[signs[c]] = float(s[last:i])

    return timedelta(**build)


def _duration(s: str) -> timedelta:
    if not s.startswith('P'):
        raise ValueError(f'"{s}" is not in a correct duration format')

    parts = s[1:].split('T')
    if len(parts) > 1:
        return _build_duration(parts[0], date_signs) + _build_duration(parts[1], time_signs)

    return _build_duration(parts[0], date_signs)


def _hostname(s: str) -> str:
    if not FQDN(s).is_valid:
        raise ValueError(f'"{s}" is not a valid hostname')

    return s


DEFAULT_FORMATS: dict[str, Callable[[str], Any]] = {
    'uuid': lambda s: uuid.UUID(s),
    'date-time': datetime.fromisoformat,
    'time': time.fromisoformat,
    'date': lambda s: datetime.strptime(s, '%Y-%m-%d').date(),
    'duration': _duration,
    'email': _email,
    'ipv4': ipaddress.IPv4Address,
    'ipv6': ipaddress.IPv6Address,
    'hostname': _hostname,
    'binary': base64.b64decode
}


def validate_string(obj, schema: dict, extended_formats: Optional[dict] = None):
    if not isinstance(obj, str):
        raise ValueError('value is not a string')

    _length(obj, schema)
    _pattern(obj, schema)

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


def _pattern(s: str, schema: dict):
    if 'pattern' in schema and not bool(re.fullmatch(schema['pattern'], s)):
        raise ValueError('value does not comply with the pattern')


def _length(s: str, schema: dict):
    if 'minLength' in schema and len(s) < schema['minLength']:
        raise ValueError(f"min length should be {schema['minLength']}, got {len(s)}")

    if 'maxLength' in schema and len(s) > schema['maxLength']:
        raise ValueError(f"max length should be {schema['maxLength']}, got {len(s)}")
