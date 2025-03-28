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

from beartype.typing import NoReturn
import pytest

from fcp.encoding import PackedEncoder, PackedEncoderContext, Value

from fcp.specs.struct import Struct
from fcp.specs.impl import Impl
from fcp.specs.struct_field import StructField
from fcp.specs.metadata import MetaData
from fcp.specs.type import BuiltinType, StructType
from fcp.specs.v2 import FcpV2


def _create_default_metadata() -> "MetaData":
    return MetaData(
        line=1,
        end_line=1,
        column=1,
        end_column=1,
        start_pos=1,
        end_pos=1,
        filename="default.fcp",
    )  # type: ignore


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
        meta=_create_default_metadata(),
    )


def test_packed_encoding(example_struct: Struct) -> NoReturn:
    example_extension = make_example_extension("A")
    fcp = FcpV2(structs=[example_struct], impls=[example_extension])

    packed_encoding = PackedEncoder(fcp, PackedEncoderContext())
    assert packed_encoding.generate(example_extension) == [
        Value("s1", BuiltinType("u32"), bitstart=0, bitlength=32),
        Value("s2", BuiltinType("u16"), bitstart=32, bitlength=16),
    ]


def test_struct(example_struct: Struct) -> NoReturn:
    b_struct = Struct(
        name="B",
        fields=[
            StructField(
                name="s1",
                field_id=0,
                type=StructType("A"),
            ),
            StructField(name="s2", field_id=1, type=BuiltinType("u8")),
        ],
    )
    example_extension = make_example_extension("B")
    fcp = FcpV2(structs=[example_struct, b_struct], impls=[example_extension])

    packed_encoding = PackedEncoder(fcp, PackedEncoderContext)

    assert packed_encoding.generate(example_extension) == [
        Value("s1::s1", BuiltinType("u32"), bitstart=0, bitlength=32),
        Value("s1::s2", BuiltinType("u16"), bitstart=32, bitlength=16),
        Value("s2", BuiltinType("u8"), bitstart=48, bitlength=8),
    ]
