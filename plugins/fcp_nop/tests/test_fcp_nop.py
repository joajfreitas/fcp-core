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
                        "type": {"name": "u32", "type": "unsigned"},
                        "unit": "C",
                    },
                    {
                        "name": "timestamp",
                        "field_id": 1,
                        "type": {"name": "u32", "type": "unsigned"},
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
                            "name": "Temperature",
                            "type": "Struct",
                        },
                    },
                    {
                        "name": "sensor_state",
                        "field_id": 1,
                        "type": {"name": "SensorState", "type": "Enum"},
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
        "impls": [
            {
                "name": "Temperature",
                "protocol": "default",
                "type": "Temperature",
                "fields": {},
                "signals": [],
            },
            {
                "name": "SensorInformation",
                "protocol": "default",
                "type": "SensorInformation",
                "fields": {},
                "signals": [],
            },
        ],
        "services": [],
        "devices": [],
        "version": "3.0",
    }
    assert json.loads(results[0].get("contents")) == txt
