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

import re
import os
from pathlib import Path
import pytest

base_dir = os.path.abspath(__file__).replace("/test.py", "")
cwd = os.getcwd().split("/")[-1]


def get_path(test_name: str) -> str:
    return f"{base_dir}/{test_name}"


EXPECTED_DEVICE_SERVICES = {
    "dash": {
        "can": {"change_led_status", "snake_leds"},
    },
    "suspot": {"can": {"calibrate_pots"}},
}

TEST_PARAMS = [
    (device, protocol, services)
    for device, protocols in EXPECTED_DEVICE_SERVICES.items()
    for protocol, services in protocols.items()
]


@pytest.mark.parametrize("device_name, protocol, expected_services", TEST_PARAMS)  # type: ignore
def test_all_generated_files_strictly_match_fcp(
    device_name: str, protocol: str, expected_services: set[str]
) -> None:
    output_path = get_path("generated_code")

    device_files = list(Path(output_path).glob(f"{device_name}_{protocol}_rpc.h"))

    assert len(device_files) > 0, f"No generated files found for {device_name}!"

    for filepath in device_files:
        with filepath.open("r") as file:
            generated_code = file.read()

        regex_pattern = rf"{device_name}_{protocol}_service_handle_([a-zA-Z0-9_]+)\("
        found_services = set(re.findall(regex_pattern, generated_code))

        assert found_services == expected_services, (
            f"Service mismatch in {filepath.name}! "
            f"Extra or missing services: {found_services ^ expected_services}"
        )
