# ruff: noqa: D103

import serde
import serde.json
import pytest
from fcp import FcpV2

from beartype.typing import Dict, Any


@pytest.fixture  # type: ignore
def fcp_v2() -> FcpV2:
    return FcpV2(structs=[], enums=[], impls=[], version="3.0")


@pytest.fixture  # type: ignore
def fcp_v2_dict() -> Dict[str, Any]:
    return {
        "structs": [],
        "enums": [],
        "impls": [],
        "services": [],
        "version": "3.0",
    }


@pytest.fixture  # type: ignore
def fcp_v2_json() -> str:
    return '{"structs": [], "enums": [], "impls": [], "services": [], "version": "3.0"}'


def test_fcp_v2_init(fcp_v2: FcpV2) -> None:
    assert fcp_v2 is not None


def test_fcp_v2_to_json(fcp_v2: FcpV2) -> None:
    assert (
        serde.json.to_json(fcp_v2)
        == '{"structs":[],"enums":[],"impls":[],"services":[],"version":"3.0"}'
    )


def test_fcp_v2_to_dict(fcp_v2: FcpV2) -> None:
    assert serde.to_dict(fcp_v2) == {
        "structs": [],
        "enums": [],
        "impls": [],
        "services": [],
        "version": "3.0",
    }


def test_v2_dict_to_fcp(fcp_v2: FcpV2, fcp_v2_dict: Dict[str, Any]) -> None:
    fcp_v2_from_dict = serde.from_dict(FcpV2, fcp_v2_dict)
    assert serde.to_dict(fcp_v2) == serde.to_dict(fcp_v2_from_dict)


def test_v2_json_to_fcp(fcp_v2: FcpV2, fcp_v2_json: str) -> None:
    assert fcp_v2 == serde.json.from_json(FcpV2, fcp_v2_json)
