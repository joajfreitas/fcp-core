# ruff: noqa: D103 D100

import tempfile
import json
from pathlib import Path
from beartype.typing import NoReturn

from fcp.v2_parser import get_fcp

from fcp_nop import Generator


def test_fcp_nop() -> NoReturn:

    fcp_config = """version: "3"

struct Temperature {
    temperature @0 : u32 | unit("C"),
    timestamp @1 : u32 | unit("s"),
}

/*this is a comment*/
enum SensorState {
    Off = 0,
    On = 1,
    Error = 2,
}

struct SensorInformation {
    temperature @ 0: Temperature,
    sensor_state @ 1: SensorState,
}
    """

    tmp = tempfile.NamedTemporaryFile()
    with open(tmp.name, "w") as fp:
        fp.write(fcp_config)

    fcp_v2, _ = get_fcp(Path(tmp.name)).unwrap()

    generator = Generator()
    results = generator.generate(fcp_v2, {"output": "output.dbc"})

    txt = {
        "structs": [
            {
                "name": "Temperature",
                "fields": [
                    {
                        "name": "temperature",
                        "field_id": 0,
                        "type": {"BuiltinType": {"name": "u32"}},
                        "unit": "C",
                    },
                    {
                        "name": "timestamp",
                        "field_id": 1,
                        "type": {"BuiltinType": {"name": "u32"}},
                        "unit": "s",
                    },
                ],
            },
            {
                "name": "SensorInformation",
                "fields": [
                    {
                        "name": "temperature",
                        "field_id": 0,
                        "type": {
                            "ComposedType": {
                                "name": "Temperature",
                                "category": "Struct",
                            }
                        },
                    },
                    {
                        "name": "sensor_state",
                        "field_id": 1,
                        "type": {
                            "ComposedType": {"name": "SensorState", "category": "Enum"}
                        },
                    },
                ],
            },
        ],
        "enums": [
            {
                "name": "SensorState",
                "enumeration": [
                    {"name": "Off", "value": 0},
                    {"name": "On", "value": 1},
                    {"name": "Error", "value": 2},
                ],
            }
        ],
        "impls": [],
        "services": [],
        "version": "3.0",
    }
    assert json.loads(results[0].get("contents")) == txt
