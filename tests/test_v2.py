"""Copyright (c) 2024 the fcp AUTHORS.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# ruff: noqa: D103 D100

import serde
import serde.json
import pytest
from fcp.specs.v2 import FcpV2

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
