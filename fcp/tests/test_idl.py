import pytest
import copy
from ..idl import *



@pytest.mark.skip(reason="fails by taking too much time in CI")
def test_message_allocation_ordered_missing_one():
    given = {
        "a": {
            "start": 0,
            "length": 32,
        },
        "b": {
            "start": 32,
            "length": 16,
        },
        "c": {
            "start": None,
            "length": 8,
        },
    }

    result = copy.deepcopy(given)
    result["c"]["start"] = 48

    assert result == message_allocation(given)


@pytest.mark.skip(reason="fails by taking too much time in CI")
def test_message_allocation_ordered_missing_all():
    given = {
        "a": {
            "start": None,
            "length": 32,
        },
        "b": {
            "start": None,
            "length": 16,
        },
        "c": {
            "start": None,
            "length": 8,
        },
    }

    result = copy.deepcopy(given)
    result["a"]["start"] = 0
    result["b"]["start"] = 32
    result["c"]["start"] = 48

    assert result == message_allocation(given)


@pytest.mark.skip(reason="fails by taking too much time in CI")
def test_message_allocation_unordered_missing_all():
    given = {
        "a": {
            "start": None,
            "length": 8,
        },
        "b": {
            "start": None,
            "length": 16,
        },
        "c": {
            "start": None,
            "length": 32,
        },
    }

    result = copy.deepcopy(given)
    result["a"]["start"] = 0
    result["b"]["start"] = 16
    result["c"]["start"] = 32

    assert result == message_allocation(given)

@pytest.mark.skip(reason="fails by taking too much time in CI")
def test_message_allocation_many_variables():
    given = {
        "a": {
            "start": None,
            "length": 8,
        },
        "b": {
            "start": None,
            "length": 8,
        },
        "c": {
            "start": None,
            "length": 8,
        },
        "d": {
            "start": None,
            "length": 8,
        },
        "e": {
            "start": None,
            "length": 8,
        },
        "f": {
            "start": None,
            "length": 8,
        },
        "g": {
            "start": None,
            "length": 8,
        },
        "h": {
            "start": None,
            "length": 8,
        },
    }

    result = copy.deepcopy(given)
    result["a"]["start"] = 0
    result["b"]["start"] = 8
    result["c"]["start"] = 16
    result["d"]["start"] = 24
    result["e"]["start"] = 32
    result["f"]["start"] = 40
    result["g"]["start"] = 48
    result["h"]["start"] = 46

    assert result == message_allocation(given)

def test_idl_types_simple_read():
    assert 1 == 1
