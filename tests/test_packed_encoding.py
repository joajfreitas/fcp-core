# ruff: noqa: D103

from beartype.typing import NoReturn
import pytest

from fcp.encoding import PackedEncoder, Value

from fcp.specs.struct import Struct
from fcp.specs.impl import Impl
from fcp.specs.struct_field import StructField
from fcp.specs.metadata import MetaData
from fcp.specs.type import BuiltinType, ComposedType
from fcp.specs.v2 import FcpV2


@pytest.fixture  # type: ignore
def example_struct() -> Struct:
    return Struct(
        name="A",
        fields=[
            StructField(
                name="s1",
                field_id=0,
                type=BuiltinType("u32"),
            ),
            StructField(
                name="s2",
                field_id=1,
                type=BuiltinType("u16"),
            ),
        ],
    )


def make_example_extension(type: str) -> Impl:
    return Impl(
        name="A",
        protocol="can",
        type=type,
        fields={},
        signals=[],
        meta=MetaData.default_metadata(),
    )


def test_packed_encoding(example_struct: Struct) -> NoReturn:
    example_extension = make_example_extension("A")
    fcp = FcpV2(structs=[example_struct], impls=[example_extension])

    packed_encoding = PackedEncoder(fcp)
    assert packed_encoding.generate(example_extension) == [
        Value("s1", BuiltinType("u32"), bitstart=0, bitlength=32),
        Value("s2", BuiltinType("u16"), bitstart=32, bitlength=16),
    ]


def test_struct(example_struct: Struct) -> NoReturn:
    b_struct = Struct(
        name="B",
        fields=[
            StructField(name="s1", field_id=0, type=ComposedType("A")),
            StructField(name="s2", field_id=1, type=BuiltinType("u8")),
        ],
    )
    example_extension = make_example_extension("B")
    fcp = FcpV2(structs=[example_struct, b_struct], impls=[example_extension])

    packed_encoding = PackedEncoder(fcp)

    assert packed_encoding.generate(example_extension) == [
        Value("s1::s1", BuiltinType("u32"), bitstart=0, bitlength=32),
        Value("s1::s2", BuiltinType("u16"), bitstart=32, bitlength=16),
        Value("s2", BuiltinType("u8"), bitstart=48, bitlength=8),
    ]
