from beartype.typing import NoReturn
import pytest

from fcp.encoding import PackedEncoding, Value

from fcp.specs.struct import Struct
from fcp.specs.signal import Signal
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


def test_packed_encoding(example_struct: Struct) -> NoReturn:
    fcp = FcpV2(structs=[example_struct])

    packed_encoding = PackedEncoding(fcp)
    assert packed_encoding.generate(example_struct) == [
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

    fcp = FcpV2(structs=[example_struct, b_struct])

    packed_encoding = PackedEncoding(fcp)

    assert packed_encoding.generate(b_struct) == [
        Value("A::s1", bitstart=0, bitlength=32),
        Value("A::s2", bitstart=32, bitlength=16),
        Value("s2", bitstart=48, bitlength=8),
    ]
