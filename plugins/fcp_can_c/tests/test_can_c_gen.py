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

import pytest
import os
import subprocess
from pathlib import Path
from fcp_can_c import Generator
from fcp.parser import get_fcp


base_dir = os.path.abspath(__file__).replace("/test_can_c_gen.py", "")
cwd = os.getcwd().split("/")[-1]


def get_path(test_name: str) -> str:
    return f"{base_dir}/{test_name}"


@pytest.mark.parametrize(
    "test_name",
    [
        "001_basic_struct",
        #"002_nested_enum",
        "003_msg_scheduling",
        "004_little_endian",
        "005_big_endian"
        "006_rpc_support",
    ],,
    ],
)  # type: ignore
def test_can_c_gen(test_name: str) -> None:
    fcp_v2 = get_fcp(Path(get_path(test_name) + "/test.fcp")).unwrap()
    generator = Generator()

    # Use test_name in the output path for generated files
    output_path = get_path(test_name) + "/generated_code"
    generator.gen(fcp_v2, None, None, os.path.join("tests", output_path))

    # List contents of the directory before running make
    for root, _, files in os.walk(output_path):
        for name in files:
            print(os.path.join(root, name))

    print("------->", os.getcwd())
    result = subprocess.run(
        ["make", "-C", os.path.join(get_path(test_name)), "run_tests"],
        capture_output=True,
        text=True,
    )

    # Print captured stdout and stderr
    print("stdout:", result.stdout)
    print("stderr:", result.stderr)
    assert result.returncode == 0
