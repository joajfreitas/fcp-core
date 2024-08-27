import pytest
from fcp import FcpV2
from serde.json import to_json, to_dict, from_json
from serde import from_dict


@pytest.fixture
def fcp_v2():
    return FcpV2(
        devices=[], structs=[], broadcasts=[], enums=[], logs=[], version="3.0"
    )


@pytest.fixture
def fcp_v2_dict():
    return {
        "structs": [],
        "enums": [],
        "devices": [],
        "broadcasts": [],
        "logs": [],
        "version": "3.0",
    }


@pytest.fixture
def fcp_v2_json():
    return '{"structs": [], "enums": [], "devices": [], "broadcasts": [], "logs": [], "version": "3.0"}'


def test_fcp_v2_init(fcp_v2):
    assert fcp_v2 is not None


def test_fcp_v2_to_json(fcp_v2):
    assert (
<<<<<<< HEAD
        fcp_v2.to_json()
        == '{"structs": [], "enums": [], "devices": [], "broadcasts": [], "logs": [], "version": "3.0"}'
=======
        to_json(fcp_v2)
        == '{"structs":[],"enums":[],"devices":[],"broadcasts":[],"logs":[],"version":"1.0"}'
>>>>>>> a3dc73d (Passing strict mypy rules and fixed tests for new serde)
    )


def test_fcp_v2_to_dict(fcp_v2):
    assert to_dict(fcp_v2) == {
        "structs": [],
        "enums": [],
        "devices": [],
        "broadcasts": [],
        "logs": [],
        "version": "3.0",
    }


def test_v2_dict_to_fcp(fcp_v2, fcp_v2_dict):
    fcp_v2_from_dict = from_dict(FcpV2, fcp_v2_dict)
    assert to_dict(fcp_v2) == to_dict(fcp_v2_from_dict)


def test_v2_json_to_fcp(fcp_v2, fcp_v2_json):
    assert fcp_v2 == from_json(FcpV2, fcp_v2_json)
