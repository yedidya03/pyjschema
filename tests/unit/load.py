import pytest

from src.load import loads


def test_number():
    schema = {'type': 'number'}

    assert loads("3", schema) == 3
    assert loads("3.1", schema) == 3.1
    assert loads("30", schema) == 30

    with pytest.raises(ValueError):
        assert loads('"asdf"', schema)

    with pytest.raises(ValueError):
        assert loads('{}', schema)

    with pytest.raises(ValueError):
        assert loads('[1,2]', schema)

    with pytest.raises(ValueError):
        assert loads(".3", schema)


class TestString:

    def test_string(self):
        schema = {'type': 'string'}

        assert loads('"string"', schema) == 'string'

        with pytest.raises(ValueError):
            assert loads('"asdf"', schema)

        with pytest.raises(ValueError):
            assert loads('{}', schema)

        with pytest.raises(ValueError):
            assert loads('[1,2]', schema)

        with pytest.raises(ValueError):
            assert loads(".3", schema)

    def test_uuid(self):
        pass


def test_bool():
    pass


def test_null():
    pass


def test_array():
    pass


def test_object():
    pass


def test_loads():
    schema = {
      "type": "object",
      "title": "GetInfoArgs",
      "properties": {
          'number': {
              'type': 'number'
          },
          'array': {
              'type': 'array',
              'items': {
                  'type': 'string'
              }
          }
      }
    }

    loads('{"number": 12.3}', schema)
    with pytest.raises(ValueError):
        loads('{"number": "12.3"}', schema)

    loads('{"number": 12.3, "array": []}', schema)
    loads('{"number": 12.3, "array": ["a", "b"]}', schema)
    with pytest.raises(ValueError):
        loads('{"number": 12.3, "array": ["a", 2]}', schema)

