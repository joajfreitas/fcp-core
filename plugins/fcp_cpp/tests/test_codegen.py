# Copyright (c) 2024 the fcp AUTHORS.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# ruff: noqa: D103 D100

import os
from pathlib import Path
from beartype.typing import List, Dict, Any

from fcp.v2_parser import get_fcp
from fcp.specs.v2 import FcpV2
from fcp_cpp import Generator
from fcp.maybe import Some, Nothing, Maybe
from fcp.serde import encode as serde_encode
from fcp.reflection import get_reflection_schema

from .cc_binary import cc_binary, InMemoryFile, InMemoryBinaryFile, File, Source

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def _handle_file(result: Dict[str, str]) -> List[Source]:
    path: Path = Path(result.get("path"))  # type: ignore
    return [InMemoryFile(path.name, str(result.get("contents")))]


def _handle_print(result: Dict[str, str]) -> List[Source]:
    print(result.get("contents"))
    return []


def handle_result(result: Dict[str, str]) -> List[Source]:
    if result.get("type") == "file":
        return _handle_file(result)
    elif result.get("type") == "print":
        return _handle_print(result)
    else:
        raise ValueError(f"Cannot handle result of type: {result.get('type')}")


def match_result(
    results: List[Dict[str, Any]], **kwargs: Dict[Any, Any]
) -> Maybe[Dict[str, Any]]:
    for result in results:
        match = True
        for kwarg in kwargs.keys():
            if kwarg in result.keys() and result[kwarg] == kwargs[kwarg]:
                continue
            else:
                match = False

        if match:
            return Some(result)

    return Nothing()


def get_fcp_config(name: str) -> str:
    config_dir = os.path.join(THIS_DIR, "schemas")
    return os.path.join(config_dir, name + ".fcp")


def get_fcp_reflection() -> FcpV2:
    return get_reflection_schema().unwrap()[0]


def test_codegen() -> None:
    fcp_v2, _ = get_fcp(Path(get_fcp_config("test"))).unwrap()
    generator = Generator()

    fcp_sources = []
    for result in generator.generate(fcp_v2, {"output": "/tmp/fcp"}):
        fcp_sources += handle_result(result)

    cc_binary(
        name="test",
        srcs=[
            File(Path(THIS_DIR) / f"test.cpp"),
        ],
        headers=fcp_sources,
        dynamic_libraries=["gtest_main", "gtest"],
    )


def test_dynamic_serialization() -> None:
    fcp_v2, _ = get_fcp(Path(get_fcp_config("test"))).unwrap()
    generator = Generator()

    fcp_sources = []
    for result in generator.generate(fcp_v2, {"output": "/tmp/fcp"}):
        fcp_sources += handle_result(result)

    cc_binary(
        name="test_dynamic",
        srcs=[
            File(Path(THIS_DIR) / f"test_dynamic.cpp"),
        ],
        headers=[
            InMemoryBinaryFile(
                "output.bin",
                serde_encode(get_fcp_reflection(), "Fcp", fcp_v2.reflection()),
            ),
        ]
        + fcp_sources,
        dynamic_libraries=["gtest_main", "gtest"],
    )


def test_can_codegen() -> None:
    fcp_v2, _ = get_fcp(Path(get_fcp_config("test"))).unwrap()
    generator = Generator()

    fcp_sources = []
    for result in generator.generate(fcp_v2, {"output": "/tmp/fcp"}):
        fcp_sources += handle_result(result)

    cc_binary(
        name="test",
        srcs=[
            File(Path(THIS_DIR) / f"test_can.cpp"),
        ],
        headers=[
            InMemoryBinaryFile(
                "output.bin",
                serde_encode(get_fcp_reflection(), "Fcp", fcp_v2.reflection()),
            )
        ]
        + fcp_sources,
        dynamic_libraries=["gtest_main", "gtest"],
    )
