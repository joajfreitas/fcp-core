import pytest
from beartype.typing import NoReturn

from fcp_dbc import Generator

from fcp import FcpV2
from fcp.specs.struct import Struct
from fcp.specs.signal import Signal
from fcp.specs.metadata import MetaData
from fcp.specs.extension import Extension


@pytest.fixture  # type: ignore
def fcp_v2() -> FcpV2:
    return FcpV2(
        structs=[
            Struct(
                name="A",
                signals=[
                    Signal(
                        name="s1",
                        field_id=0,
                        type="u8",
                        meta=MetaData.default_metadata(),
                    ),
                    Signal(
                        name="s2",
                        field_id=1,
                        type="u8",
                        meta=MetaData.default_metadata(),
                    ),
                ],
            )
        ],
        extensions=[
            Extension(
                name="A",
                protocol="can",
                type="A",
                fields={"id": 10},
                signals=[],
                meta=MetaData.default_metadata(),
            )
        ],
    )


def test_dbc_generator(fcp_v2: FcpV2) -> NoReturn:
    generator = Generator()
    results = generator.generate(
        fcp_v2,
        {"output": "output.dbc"},
    )

    contents = results[0].get("contents")

    lines = [line for line in contents.split("\r\n") if line != ""]

    dbc = """BO_ 10 A: 8 Vector__XXX
 SG_ s2 : 8|8@1+ (1,0) [0|0] "" Vector__XXX
 SG_ s1 : 0|8@1+ (1,0) [0|0] "" Vector__XXX"""

    assert dbc == "\n".join(lines[-3:])
