# ruff: noqa: D103 D100

import os
from pathlib import Path
from hypothesis import given, settings
from hypothesis.strategies import text, integers, floats, text, characters, lists

from fcp.serde import encode, decode
from fcp.v2_parser import get_fcp

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def get_fcp_config(scope: str, name: str) -> Path:
    config_dir = os.path.join(THIS_DIR, "schemas", scope)
    return Path(os.path.join(config_dir, name + ".fcp"))


def test_encoding_single_byte_types() -> None:
    fcp_v2, _ = get_fcp(get_fcp_config("syntax", "001_basic_struct")).unwrap()

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
    fcp_v2, _ = get_fcp(get_fcp_config("syntax", "001_basic_struct")).unwrap()

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
    fcp_v2, _ = get_fcp(get_fcp_config("syntax", "001_basic_struct")).unwrap()

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
    fcp_v2, _ = get_fcp(get_fcp_config("syntax", "001_basic_struct")).unwrap()

    encoded = encode(fcp_v2, "S5", {"s0": "hello"})

    assert encoded == bytearray(
        [0x05, 0x00, 0x00, 0x00, ord("h"), ord("e"), ord("l"), ord("l"), ord("o")]
    )


def test_encoding_struct_composition() -> None:
    fcp_v2, _ = get_fcp(get_fcp_config("syntax", "004_struct_composition")).unwrap()

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
    fcp_v2, _ = get_fcp(get_fcp_config("syntax", "007_simple_array_type")).unwrap()

    encoded = encode(fcp_v2, "A", {"field1": [1, 2, 3, 4]})

    assert encoded == bytearray([0x01, 0x02, 0x03, 0x04])


def test_encoding_dynamic_array() -> None:
    fcp_v2, _ = get_fcp(get_fcp_config("syntax", "008_dynamic_array")).unwrap()

    encoded = encode(fcp_v2, "S1", {"field1": [1, 2, 3]})

    assert encoded == bytearray([0x3, 0x0, 0x0, 0x0, 0x1, 0x2, 0x3])


def test_decoding_single_byte_types() -> None:
    fcp_v2, _ = get_fcp(get_fcp_config("syntax", "001_basic_struct")).unwrap()

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
    fcp_v2, _ = get_fcp(get_fcp_config("syntax", "001_basic_struct")).unwrap()

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
    fcp_v2, _ = get_fcp(get_fcp_config("syntax", "001_basic_struct")).unwrap()

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
    fcp_v2, _ = get_fcp(get_fcp_config("syntax", "001_basic_struct")).unwrap()

    decoded = decode(
        fcp_v2,
        "S5",
        bytearray(
            [0x05, 0x00, 0x00, 0x00, ord("h"), ord("e"), ord("l"), ord("l"), ord("o")]
        ),
    )

    assert decoded == {"s0": "hello"}


def test_decoding_struct_composition() -> None:
    fcp_v2, _ = get_fcp(get_fcp_config("syntax", "004_struct_composition")).unwrap()

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
    fcp_v2, _ = get_fcp(get_fcp_config("syntax", "007_simple_array_type")).unwrap()

    decoded = decode(
        fcp_v2,
        "A",
        bytearray([0x01, 0x02, 0x03, 0x04]),
    )

    assert decoded == {"field1": [1, 2, 3, 4]}


def test_decoding_dynamic_array() -> None:
    fcp_v2, _ = get_fcp(get_fcp_config("syntax", "008_dynamic_array")).unwrap()

    decoded = decode(
        fcp_v2,
        "S1",
        bytearray([0x3, 0x0, 0x0, 0x0, 0x1, 0x2, 0x3]),
    )

    assert decoded == {"field1": [1, 2, 3]}


@settings(max_examples=20)  # type: ignore
@given(integers(min_value=0, max_value=255))  # type: ignore
def test_roundtrip_decoding_single_byte_types(integer) -> None:
    fcp_v2, _ = get_fcp(get_fcp_config("syntax", "001_basic_struct")).unwrap()

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
def test_roundtrip_decoding_8_byte_types(integer1, integer2) -> None:
    fcp_v2, _ = get_fcp(get_fcp_config("syntax", "001_basic_struct")).unwrap()

    data = {
        "s0": integer1,
        "s1": integer2,
    }
    encoded = encode(fcp_v2, "S3", data)

    decoded = decode(fcp_v2, "S3", encoded)

    assert decoded == data


@settings(max_examples=20)  # type: ignore
@given(f1=floats(width=32, allow_nan=False), f2=floats(width=64, allow_nan=False))  # type: ignore
def test_roundtrip_decoding_floating_point_types(f1, f2) -> None:
    fcp_v2, _ = get_fcp(get_fcp_config("syntax", "001_basic_struct")).unwrap()

    data = {
        "s0": f1,
        "s1": f2,
    }

    encoded = encode(fcp_v2, "S4", data)

    assert decode(fcp_v2, "S4", encoded) == data


@settings(max_examples=20)  # type: ignore
@given(text(alphabet=characters(codec="ascii"), max_size=4096))  # type: ignore
def test_roundtrip_decoding_str(t) -> None:
    fcp_v2, _ = get_fcp(get_fcp_config("syntax", "001_basic_struct")).unwrap()

    data = {"s0": t}
    encoded = encode(fcp_v2, "S5", data)

    decoded = decode(fcp_v2, "S5", encoded)
    assert decoded == data


@settings(max_examples=20)  # type: ignore
@given(lists(integers(min_value=0, max_value=255), min_size=4, max_size=4))  # type: ignore
def test_roundtrip_decoding_simple_array_type(array) -> None:
    fcp_v2, _ = get_fcp(get_fcp_config("syntax", "007_simple_array_type")).unwrap()

    data = {"field1": array}
    encoded = encode(fcp_v2, "A", {"field1": [1, 2, 3, 4]})

    assert decode(fcp_v2, "S1", encoded) == data


@settings(max_examples=20)  # type: ignore
@given(lists(integers(min_value=0, max_value=255), max_size=4092))  # type: ignore
def test_roundtrip_decoding_simple_array_type(array) -> None:
    fcp_v2, _ = get_fcp(get_fcp_config("syntax", "008_dynamic_array")).unwrap()

    data = {"field1": array}
    encoded = encode(fcp_v2, "S1", data)

    assert decode(fcp_v2, "S1", encoded) == data
