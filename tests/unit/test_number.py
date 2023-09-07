import pytest

from pyjschema.load import loads


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


def test_multiply_of():
    schema = {'type': 'number', 'multipleOf': 3}

    assert loads("3", schema) == 3
    with pytest.raises(ValueError):
        loads("5", schema)

    with pytest.raises(ValueError):
        loads("3.5", schema)

    schema = {'type': 'number', 'multipleOf': 3.5}
    assert loads("7", schema) == 7


def test_range():
    schema = {'type': 'number', 'minimum': 3}
    assert loads("3", schema) == 3
    assert loads("4", schema) == 4
    with pytest.raises(ValueError):
        loads("2", schema)

    schema = {'type': 'number', 'exclusiveMinimum': 3}
    assert loads("4", schema) == 4
    with pytest.raises(ValueError):
        loads("3", schema)

    schema = {'type': 'number', 'maximum': 3}
    assert loads("3", schema) == 3
    assert loads("2", schema) == 2
    with pytest.raises(ValueError):
        loads("4", schema)

    schema = {'type': 'number', 'exclusiveMaximum': 3}
    assert loads("2", schema) == 2
    with pytest.raises(ValueError):
        loads("4", schema)
