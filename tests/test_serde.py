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
from beartype.typing import List
from hypothesis import given, settings
from hypothesis.strategies import (
    text,
    integers,
    floats,
    characters,
    lists,
    booleans,
)

from fcp.serde import encode, decode
from fcp.v2_parser import get_fcp

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def get_fcp_config(scope: str, name: str) -> Path:
    config_dir = os.path.join(THIS_DIR, "schemas", scope)
    return Path(os.path.join(config_dir, name + ".fcp"))


def test_encoding_single_byte_types() -> None:
    fcp_v2 = get_fcp(get_fcp_config("syntax", "001_basic_struct")).unwrap()

    encoded = encode(
        fcp_v2,
        "S2",
        {
            "s0": 1,
            "s1": -1,
        },
    )

    assert encoded == bytearray([1, 255])


def test_encoding_8_byte_types() -> None:
    fcp_v2 = get_fcp(get_fcp_config("syntax", "001_basic_struct")).unwrap()

    encoded = encode(
        fcp_v2,
        "S3",
        {
            "s0": 1,
            "s1": -1,
        },
    )

    assert encoded == bytearray(
        # fmt: off
        [
            0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
        ]
        # fmt: on
    )


def test_encoding_floating_point_types() -> None:
    fcp_v2 = get_fcp(get_fcp_config("syntax", "001_basic_struct")).unwrap()

    encoded = encode(
        fcp_v2,
        "S4",
        {
            "s0": 1.0,
            "s1": 1.0,
        },
    )

    assert encoded == bytearray(
        [0x00, 0x00, 0x80, 0x3F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xF0, 0x3F]
    )


def test_encoding_str() -> None:
    fcp_v2 = get_fcp(get_fcp_config("syntax", "001_basic_struct")).unwrap()

    encoded = encode(fcp_v2, "S5", {"s0": "hello"})

    assert encoded == bytearray(
        [0x05, 0x00, 0x00, 0x00, ord("h"), ord("e"), ord("l"), ord("l"), ord("o")]
    )


def test_encoding_struct_composition() -> None:
    fcp_v2 = get_fcp(get_fcp_config("syntax", "004_struct_composition")).unwrap()

    encoded = encode(
        fcp_v2,
        "baz",
        {
            "var": {
                "var1": 1,
                "var2": 1,
            }
        },
    )

    assert encoded == bytearray([0x01, 0x01])


def test_encoding_simple_array_type() -> None:
    fcp_v2 = get_fcp(get_fcp_config("syntax", "007_simple_array_type")).unwrap()

    encoded = encode(fcp_v2, "S1", {"field1": [1, 2, 3, 4]})

    assert encoded == bytearray([0x01, 0x02, 0x03, 0x04])


def test_encoding_dynamic_array() -> None:
    fcp_v2 = get_fcp(get_fcp_config("syntax", "008_dynamic_array")).unwrap()

    encoded = encode(fcp_v2, "S1", {"field1": [1, 2, 3]})

    assert encoded == bytearray([0x3, 0x0, 0x0, 0x0, 0x1, 0x2, 0x3])


def test_encoding_optional_with_value() -> None:
    fcp_v2 = get_fcp(get_fcp_config("syntax", "009_optional")).unwrap()

    encoded = encode(fcp_v2, "S1", {"field1": 1})

    assert encoded == bytearray([0x1, 0x1])


def test_encoding_optional_with_none() -> None:
    fcp_v2 = get_fcp(get_fcp_config("syntax", "009_optional")).unwrap()

    encoded = encode(fcp_v2, "S1", {"field1": None})

    assert encoded == bytearray([0x0])


def test_decoding_single_byte_types() -> None:
    fcp_v2 = get_fcp(get_fcp_config("syntax", "001_basic_struct")).unwrap()

    decoded = decode(
        fcp_v2,
        "S2",
        bytearray([1, 255]),
    )

    assert decoded == {
        "s0": 1,
        "s1": -1,
    }


def test_decoding_8_byte_types() -> None:
    fcp_v2 = get_fcp(get_fcp_config("syntax", "001_basic_struct")).unwrap()

    decoded = decode(
        fcp_v2,
        "S3",
        # fmt: off
        bytearray(
            [
                0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
            ]
        # fmt: on
        ),
    )

    assert decoded == {
        "s0": 1,
        "s1": -1,
    }


def test_decoding_floating_point_types() -> None:
    fcp_v2 = get_fcp(get_fcp_config("syntax", "001_basic_struct")).unwrap()

    decoded = decode(
        fcp_v2,
        "S4",
        bytearray(
            [0x00, 0x00, 0x80, 0x3F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xF0, 0x3F]
        ),
    )

    assert decoded == {
        "s0": 1.0,
        "s1": 1.0,
    }


def test_decoding_str() -> None:
    fcp_v2 = get_fcp(get_fcp_config("syntax", "001_basic_struct")).unwrap()

    decoded = decode(
        fcp_v2,
        "S5",
        bytearray(
            [0x05, 0x00, 0x00, 0x00, ord("h"), ord("e"), ord("l"), ord("l"), ord("o")]
        ),
    )

    assert decoded == {"s0": "hello"}


def test_decoding_struct_composition() -> None:
    fcp_v2 = get_fcp(get_fcp_config("syntax", "004_struct_composition")).unwrap()

    decoded = decode(
        fcp_v2,
        "baz",
        bytearray([0x01, 0x01]),
    )

    assert decoded == {
        "var": {
            "var1": 1,
            "var2": 1,
        }
    }


def test_decoding_simple_array_type() -> None:
    fcp_v2 = get_fcp(get_fcp_config("syntax", "007_simple_array_type")).unwrap()

    decoded = decode(
        fcp_v2,
        "S1",
        bytearray([0x01, 0x02, 0x03, 0x04]),
    )

    assert decoded == {"field1": [1, 2, 3, 4]}


def test_decoding_dynamic_array() -> None:
    fcp_v2 = get_fcp(get_fcp_config("syntax", "008_dynamic_array")).unwrap()

    decoded = decode(
        fcp_v2,
        "S1",
        bytearray([0x3, 0x0, 0x0, 0x0, 0x1, 0x2, 0x3]),
    )

    assert decoded == {"field1": [1, 2, 3]}


def test_decoding_optional_with_value() -> None:
    fcp_v2 = get_fcp(get_fcp_config("syntax", "009_optional")).unwrap()

    decoded = decode(
        fcp_v2,
        "S1",
        bytearray([0x1, 0x1]),
    )

    assert decoded == {"field1": 1}


def test_decoding_optional_with_none() -> None:
    fcp_v2 = get_fcp(get_fcp_config("syntax", "009_optional")).unwrap()

    decoded = decode(
        fcp_v2,
        "S1",
        bytearray([0x0]),
    )

    assert decoded == {"field1": None}


@settings(max_examples=20)  # type: ignore
@given(integers(min_value=0, max_value=255))  # type: ignore
def test_roundtrip_decoding_single_byte_types(integer: int) -> None:
    fcp_v2 = get_fcp(get_fcp_config("syntax", "001_basic_struct")).unwrap()

    data = {
        "s0": integer,
        "s1": 1,
    }
    encoded = encode(fcp_v2, "S2", data)

    decoded = decode(fcp_v2, "S2", encoded)

    assert decoded == data


@settings(max_examples=20)  # type: ignore
@given(
    integer1=integers(min_value=0, max_value=2**64 - 1),
    integer2=integers(min_value=-(2**63 - 1), max_value=2**63),
)  # type: ignore
def test_roundtrip_decoding_8_byte_types(integer1: int, integer2: int) -> None:
    fcp_v2 = get_fcp(get_fcp_config("syntax", "001_basic_struct")).unwrap()

    data = {
        "s0": integer1,
        "s1": integer2,
    }
    encoded = encode(fcp_v2, "S3", data)

    decoded = decode(fcp_v2, "S3", encoded)

    assert decoded == data


@settings(max_examples=20)  # type: ignore
@given(f1=floats(width=32, allow_nan=False), f2=floats(width=64, allow_nan=False))  # type: ignore
def test_roundtrip_decoding_floating_point_types(f1: float, f2: float) -> None:
    fcp_v2 = get_fcp(get_fcp_config("syntax", "001_basic_struct")).unwrap()

    data = {
        "s0": f1,
        "s1": f2,
    }

    encoded = encode(fcp_v2, "S4", data)

    assert decode(fcp_v2, "S4", encoded) == data


@settings(max_examples=20)  # type: ignore
@given(text(alphabet=characters(codec="ascii"), max_size=4096))  # type: ignore
def test_roundtrip_decoding_str(t: str) -> None:
    fcp_v2 = get_fcp(get_fcp_config("syntax", "001_basic_struct")).unwrap()

    data = {"s0": t}
    encoded = encode(fcp_v2, "S5", data)

    decoded = decode(fcp_v2, "S5", encoded)
    assert decoded == data


@settings(max_examples=20)  # type: ignore
@given(lists(integers(min_value=0, max_value=255), min_size=4, max_size=4))  # type: ignore
def test_roundtrip_decoding_simple_array_type(array: List[int]) -> None:
    fcp_v2 = get_fcp(get_fcp_config("syntax", "007_simple_array_type")).unwrap()

    data = {"field1": array}
    encoded = encode(fcp_v2, "S1", data)

    assert decode(fcp_v2, "S1", encoded) == data


@settings(max_examples=20)  # type: ignore
@given(lists(integers(min_value=0, max_value=255), max_size=4092))  # type: ignore
def test_roundtrip_decoding_simple_dynamic_array_type(array: List[int]) -> None:
    fcp_v2 = get_fcp(get_fcp_config("syntax", "008_dynamic_array")).unwrap()

    data = {"field1": array}
    encoded = encode(fcp_v2, "S1", data)

    assert decode(fcp_v2, "S1", encoded) == data


@settings(max_examples=20)  # type: ignore
@given(integers(min_value=0, max_value=255), booleans())  # type: ignore
def test_roundtrip_decoding_optional(value: int, is_some: bool) -> None:
    fcp_v2 = get_fcp(get_fcp_config("syntax", "009_optional")).unwrap()

    data = {"field1": value if is_some else None}
    encoded = encode(fcp_v2, "S1", data)

    assert decode(fcp_v2, "S1", encoded) == data
