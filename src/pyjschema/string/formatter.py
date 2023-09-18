from datetime import datetime, time, date
from ipaddress import IPv4Address, IPv6Address
from typing import Any
from uuid import UUID


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

# TODO: 'duration', 'hostname'
