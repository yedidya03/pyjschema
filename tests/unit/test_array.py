import pytest

from pyjschema.load import loads


def test_items():
    schema = {'type': 'array', 'items': {'type': 'number'}}

    assert loads(f'[1,2,3.1]', schema) == [1, 2, 3.1]
    with pytest.raises(ValueError):
        loads(f'"test1"', schema)


def test_prefix_items():
    schema = {'type': 'array', 'prefixItems': [{'type': 'number'}, {'type': 'string'}]}
    assert loads(f'[1, "D"]', schema) == [1, "D"]
    assert loads(f'[1, "D", 1]', schema) == [1, "D", 1]
    with pytest.raises(ValueError):
        loads(f'"test1"', schema)

    schema = {'type': 'array', 'prefixItems': [{'type': 'number'}, {'type': 'string'}], 'items': {'type': 'number'}}
    assert loads(f'[1, "D"]', schema) == [1, "D"]
    assert loads(f'[1, "D", 1]', schema) == [1, "D", 1]
    with pytest.raises(ValueError):
        loads(f'[1, "D", "1"]', schema)

    schema = {'type': 'array', 'prefixItems': [{'type': 'number'}, {'type': 'string'}], 'items': False}
    assert loads(f'[1, "D"]', schema) == [1, "D"]
    with pytest.raises(ValueError):
        loads(f'"test1"', schema)

    with pytest.raises(ValueError):
        loads(f'[1, "D", 1]', schema)


def test_unique():
    schema = {'type': 'array', 'items': {'type': 'number'}, 'uniqueItems': True}

    assert loads(f'[1, 2, 3, 4, 5]', schema) == [1, 2, 3, 4, 5]
    with pytest.raises(ValueError):
        loads(f'[1, 2, 3, 3, 5]', schema)


def test_contains():
    schema = {'type': 'array', 'contains': {'type': 'number'}}

    assert loads(f'["life", "universe", "everything", 42]', schema) == ["life", "universe", "everything", 42]
    assert loads(f'[1, 2, 3, 4, 5]', schema) == [1, 2, 3, 4, 5]
    with pytest.raises(ValueError):
        loads(f'["life", "universe", "everything", "forty-two"]', schema)
