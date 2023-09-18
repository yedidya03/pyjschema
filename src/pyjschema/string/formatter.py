from datetime import datetime, time, date, timedelta
from ipaddress import IPv4Address, IPv6Address
from typing import Any
from uuid import UUID

from fqdn import FQDN


class Formatter:
    """
    Formatter is a class that is defining a format of the "string" type in Json-Schema.
    Each format has a symbol that is presented in the schema (under "format") and defines the encode and decode methods
    for handling conversions between raw strings and pythonic objects of the format.
    """

    symbol: str = None

    def decode(self, raw: str) -> Any:
        """
        Decodes a raw json text to the pythonic object according to the format
        """
        raise NotImplemented

    def encode(self, data: Any) -> str:
        """
        Encodes a pythonic object to a json string according to the format.
        """
        raise NotImplemented


class UUIDFormat(Formatter):
    symbol = 'uuid'

    def encode(self, data: UUID) -> str:
        return str(data)

    def decode(self, raw: str) -> UUID:
        return UUID(raw)


class DatetimeFormat(Formatter):
    symbol = 'date-time'

    def encode(self, data: datetime) -> str:
        return data.isoformat()

    def decode(self, raw: str) -> datetime:
        return datetime.fromisoformat(raw)


class TimeFormat(Formatter):
    symbol = 'time'

    def encode(self, data: time) -> str:
        return data.isoformat()

    def decode(self, raw: str) -> time:
        return time.fromisoformat(raw)


class DateFormat(Formatter):
    symbol = 'date'

    def encode(self, data: date) -> str:
        return data.strftime('%Y-%m-%d')

    def decode(self, raw: str) -> date:
        return datetime.strptime(raw, '%Y-%m-%d').date()


class EmailFormatter(Formatter):
    symbol = 'email'

    def encode(self, data: str) -> str:
        return self._validate_email(data)

    def decode(self, raw: str) -> str:
        return self._validate_email(raw)

    @staticmethod
    def _validate_email(s: str) -> str:
        if '@' not in s:
            raise ValueError('email not valid')

        return s


class Ipv4Formatter(Formatter):
    symbol = 'ipv4'

    def encode(self, data: IPv4Address) -> str:
        return str(data)

    def decode(self, raw: str) -> IPv4Address:
        return IPv4Address(raw)


class Ipv6Formatter(Formatter):
    symbol = 'ipv6'

    def encode(self, data: IPv6Address) -> str:
        return str(data)

    def decode(self, raw: str) -> IPv6Address:
        return IPv6Address(raw)


class DurationFormatter(Formatter):
    symbol = 'duration'

    _date_signs = {'Y': 'years', 'M': 'months', 'W': 'weeks', 'D': 'days'}
    _time_signs = {'H': 'hours', 'M': 'minutes', 'S': 'seconds'}

    def decode(self, s: str) -> timedelta:
        if not s.startswith('P'):
            raise ValueError(f'"{s}" is not in a correct duration format')

        parts = s[1:].split('T')
        if len(parts) > 1:
            return self._build_duration(parts[0], self._date_signs) + self._build_duration(parts[1], self._time_signs)

        return self._build_duration(parts[0], self._date_signs)

    @staticmethod
    def _build_duration(s: str, signs: dict[str, str]) -> timedelta:
        build = {}
        last = 0
        for i, c in enumerate(s):
            if c in signs:
                build[signs[c]] = float(s[last:i])

        return timedelta(**build)

    def encode(self, data: timedelta) -> str:
        # split seconds to larger units
        seconds = data.total_seconds()
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        days, hours, minutes = map(int, (days, hours, minutes))
        seconds = round(seconds, 6)

        # build date
        date_string = ''
        if days:
            date_string = '%sD' % days

        # build time
        time_string = u'T'
        # hours
        bigger_exists = date_string or hours
        if bigger_exists:
            time_string += '{:02}H'.format(hours)
        # minutes
        bigger_exists = bigger_exists or minutes
        if bigger_exists:
            time_string += '{:02}M'.format(minutes)
        # seconds
        if seconds.is_integer():
            seconds = '{:02}'.format(int(seconds))
        else:
            # 9 chars long w/leading 0, 6 digits after decimal
            seconds = '%09.6f' % seconds
        # remove trailing zeros
        seconds = seconds.rstrip('0')
        time_string += '{}S'.format(seconds)
        return u'P' + date_string + time_string


class HostnameFormatter(Formatter):
    symbol = 'hostname'

    def decode(self, raw: str) -> str:
        return self._validate(raw)

    def encode(self, data: str) -> str:
        return self._validate(data)

    @staticmethod
    def _validate(s: str) -> str:
        if not FQDN(s).is_valid:
            raise ValueError(f'"{s}" is not a valid hostname')

        return s
