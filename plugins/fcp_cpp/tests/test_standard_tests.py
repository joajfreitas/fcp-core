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
import json
import jinja2
from pathlib import Path
import pytest
from beartype.typing import List, Dict, Any

from fcp.specs.v2 import FcpV2
from fcp_cpp import Generator
from fcp.parser import get_fcp
from fcp.specs.type import (
    Type,
    ArrayType,
    DynamicArrayType,
    OptionalType,
    EnumType,
    StringType,
    UnsignedType,
    SignedType,
    FloatType,
    DoubleType,
)
from fcp.xpath import Xpath

from .cc_binary import cc_binary, InMemoryFile, Source

THIS_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = THIS_DIR.parent.parent.parent
STANDARDIZED_TESTS_DIR = ROOT_DIR / "tests" / "standardized"


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


def to_constant(fcp: FcpV2, type: Type, value: Any) -> str:
    """Convert a value to a constant."""
    if isinstance(type, UnsignedType):
        if value[0].isdigit() or value[0] == "-":
            return str(value) + "ULL"
        else:
            return str(value)
    elif isinstance(type, SignedType):
        if not value[0].isdigit():
            return str(value)
        else:
            return str(value) + "LL"
    elif isinstance(type, FloatType):
        return str(value)
    elif isinstance(type, DoubleType):
        return str(value)
    elif isinstance(type, StringType):
        return str('"' + value + '"')
    elif isinstance(type, EnumType):
        return str("fcp::" + type.name + "::" + value)
    elif isinstance(type, ArrayType) or isinstance(type, DynamicArrayType):
        return str(
            "{"
            + ", ".join([to_constant(fcp, type.underlying_type, v) for v in value])
            + "}"
        )
    elif isinstance(type, OptionalType):
        if value is None:
            return "std::nullopt"
        else:
            return to_constant(fcp, type.underlying_type, value)
    else:
        raise ValueError(f"Unknown type: {type}")


def to_initializer(fcp: FcpV2, xpath: str, value: Any) -> str:
    struct_field = fcp.get_xpath(Xpath(xpath))
    type = struct_field.unwrap().type

    return to_constant(fcp, type, value)


def access_field(fcp: FcpV2, xpath: str) -> str:
    return ".".join(["View" + path.capitalize() + "()" for path in Xpath(xpath).path])


test_template = """
#include <gtest/gtest.h>
#include <gmock/gmock.h>
#include <iostream>
#include "fcp.h"

{% for test in suite["tests"] %}
TEST({{ suite["name"] }}, {{ test["name"] }}) {

    auto sut = fcp::{{test["datatype"]}}{};

    {% for xpath, value in test["decoded"].items() %}
    sut.{{access_field(fcp,xpath)}} = {{to_initializer(fcp, xpath, value)}};
    {% endfor %}

    auto encoded = sut.Encode().GetData();

    std::vector<std::uint8_t> expected { {%- for value in test["encoded"] -%} {{value}} {%- if not loop.last -%},{%- endif -%}{%- endfor -%} };

    EXPECT_THAT(encoded, expected);
    if (encoded != expected) {
        for (size_t i = 0; i < encoded.size(); i++) {
            std::cout << "encoded[" << i << "] = " << (int)encoded[i] << std::endl;
        }

        for (size_t i = 0; i < expected.size(); i++) {
            std::cout << "expected[" << i << "] = " << (int)expected[i] << std::endl;
        }
    }
}
{% endfor %}
"""


@pytest.mark.parametrize(
    "test_suite", json.loads((STANDARDIZED_TESTS_DIR / "fcp_tests.json").read_text())
)  # type: ignore
def test_standardized_tests(test_suite: Dict[Any, Any]) -> None:
    loader = jinja2.DictLoader({"test_template": test_template})

    env = jinja2.Environment(loader=loader)
    env.globals["to_initializer"] = to_initializer
    env.globals["access_field"] = access_field
    template = env.get_template("test_template")

    fcp_v2 = get_fcp(STANDARDIZED_TESTS_DIR / test_suite["schema"]).unwrap()

    generator = Generator()

    fcp_sources = []
    for result in generator.generate(fcp_v2, {"output": "/tmp/fcp"}):
        fcp_sources += handle_result(result)

    cc_binary(
        name="standardized_test",
        srcs=[
            InMemoryFile(
                "test.cpp",
                template.render(
                    {
                        "suite": test_suite,
                        "fcp": fcp_v2,
                    }
                ),
            ),
        ],
        headers=[] + fcp_sources,
        dynamic_libraries=["gtest_main", "gtest"],
    )
