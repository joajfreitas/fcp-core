import pytest
from fcp import FcpV2
from serde.json import to_json, from_json
from serde import from_dict, to_dict

from typing import Dict, Any


@pytest.fixture  # type: ignore
def fcp_v2() -> FcpV2:
    return FcpV2(structs=[], enums=[], version="3.0")


@pytest.fixture  # type: ignore
def fcp_v2_dict() -> Dict[str, Any]:
    return {
        "structs": [],
        "enums": [],
        "version": "3.0",
    }


@pytest.fixture  # type: ignore
def fcp_v2_json() -> str:
    return '{"structs": [], "enums": [], "devices": [], "broadcasts": [], "logs": [], "version": "3.0"}'


def test_fcp_v2_init(fcp_v2: FcpV2) -> None:
    assert fcp_v2 is not None


def test_fcp_v2_to_json(fcp_v2: FcpV2) -> None:
    assert to_json(fcp_v2) == '{"structs":[],"enums":[],"version":"3.0"}'


def test_fcp_v2_to_dict(fcp_v2: FcpV2) -> None:
    assert to_dict(fcp_v2) == {
        "structs": [],
        "enums": [],
        "version": "3.0",
    }


def test_v2_dict_to_fcp(fcp_v2: FcpV2, fcp_v2_dict: Dict[str, Any]) -> None:
    fcp_v2_from_dict = from_dict(FcpV2, fcp_v2_dict)
    assert to_dict(fcp_v2) == to_dict(fcp_v2_from_dict)


def test_v2_json_to_fcp(fcp_v2: FcpV2, fcp_v2_json: str) -> None:
    assert fcp_v2 == from_json(FcpV2, fcp_v2_json)
