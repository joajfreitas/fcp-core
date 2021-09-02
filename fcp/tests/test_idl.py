import pytest
import copy
from ..idl import *

def test_message_allocation_empty():
    assert {} == message_allocation({})

def test_message_allocation_ordered_missing_one():
    given = {
        "a": {"start": 0, "length": 32,},
        "b": {"start": 32, "length": 16,},
        "c": {"start": None, "length": 8,},
    }

    result = copy.deepcopy(given)
    result["c"] ["start"] = 48

    assert result == message_allocation(given)

def test_message_allocation_ordered_missing_all():
    given = {
        "a": {"start": None, "length": 32,},
        "b": {"start": None, "length": 16,},
        "c": {"start": None, "length": 8,},
    }

    result = copy.deepcopy(given)
    result["a"] ["start"] = 0
    result["b"] ["start"] = 32
    result["c"] ["start"] = 48

    assert result == message_allocation(given)

def test_message_allocation_unordered_missing_all():
    given = {
        "a": {"start": None, "length": 8,},
        "b": {"start": None, "length": 16,},
        "c": {"start": None, "length": 32,},
    }

    result = copy.deepcopy(given)
    result["a"] ["start"] = 0
    result["b"] ["start"] = 16
    result["c"] ["start"] = 32

    assert result == message_allocation(given)
