import pytest
from src.fcp import FcpV2


@pytest.fixture
def fcp_v2():
    return FcpV2(devices=[], structs=[], broadcasts=[], enums=[], logs=[])


@pytest.fixture
def fcp_v2_dict():
    return {
        "structs": [],
        "enums": [],
        "devices": [],
        "broadcasts": [],
        "logs": [],
        "version": "1.0",
    }


@pytest.fixture
def fcp_v2_json():
    return '{"structs": [], "enums": [], "devices": [], "broadcasts": [], "logs": [], "version": "1.0"}'


def test_fcp_v2_init(fcp_v2):
    assert fcp_v2 is not None


def test_fcp_v2_to_json(fcp_v2):
    assert (
        fcp_v2.to_json()
        == '{"structs": [], "enums": [], "devices": [], "broadcasts": [], "logs": [], "version": "1.0"}'
    )


def test_fcp_v2_to_dict(fcp_v2):
    assert fcp_v2.to_dict() == {
        "structs": [],
        "enums": [],
        "devices": [],
        "broadcasts": [],
        "logs": [],
        "version": "1.0",
    }


def test_v2_dict_to_fcp(fcp_v2, fcp_v2_dict):
    assert fcp_v2 == FcpV2.from_dict(fcp_v2_dict)


def test_v2_json_to_fcp(fcp_v2, fcp_v2_json):
    assert fcp_v2 == FcpV2.from_json(fcp_v2_json)
