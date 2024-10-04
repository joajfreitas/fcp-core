from beartype.typing import NoReturn
import pytest

from fcp.encoding import PackedEncoder, Value

from fcp.specs.struct import Struct
from fcp.specs.extension import Extension
from fcp.specs.signal import Signal
from fcp.specs.metadata import MetaData
from fcp.specs.v2 import FcpV2


@pytest.fixture  # type: ignore
def example_struct() -> Struct:
    return Struct(
        name="A",
        signals=[
            Signal(
                name="s1",
                field_id=0,
                type="u32",
            ),
            Signal(
                name="s2",
                field_id=1,
                type="u16",
            ),
        ],
    )


def make_example_extension(type: str) -> Extension:
    return Extension(
        name="A",
        protocol="can",
        type=type,
        fields={},
        signals=[],
        meta=MetaData.default_metadata(),
    )


def test_packed_encoding(example_struct: Struct) -> NoReturn:
    example_extension = make_example_extension("A")
    fcp = FcpV2(structs=[example_struct], extensions=[example_extension])

    packed_encoding = PackedEncoder(fcp)
    assert packed_encoding.generate(example_extension) == [
        Value(name="s1", bitstart=0, bitlength=32),
        Value(name="s2", bitstart=32, bitlength=16),
    ]


def test_struct(example_struct: Struct) -> NoReturn:
    b_struct = Struct(
        name="B",
        signals=[
            Signal(name="s1", field_id=0, type="A"),
            Signal(name="s2", field_id=1, type="u8"),
        ],
    )
    example_extension = make_example_extension("B")
    fcp = FcpV2(structs=[example_struct, b_struct], extensions=[example_extension])

    packed_encoding = PackedEncoder(fcp)

    assert packed_encoding.generate(example_extension) == [
        Value("s1::s1", bitstart=0, bitlength=32),
        Value("s1::s2", bitstart=32, bitlength=16),
        Value("s2", bitstart=48, bitlength=8),
    ]
