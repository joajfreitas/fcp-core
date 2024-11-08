"""Copyright (c) 2024 the fcp AUTHORS.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# ruff: noqa: D103 D100

import os
from pathlib import Path
import subprocess
import tempfile
import shutil
import pytest
from beartype.typing import List, Dict, Any

from fcp.v2_parser import get_fcp
from fcp.codegen import handle_result
from fcp_cpp import Generator
from fcp.maybe import Some, Nothing, Maybe

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def match_result(
    results: List[Dict[str, Any]], **kwargs: Dict[Any, Any]
) -> Maybe[Dict[str, Any]]:
    for result in results:
        match = True
        for kwarg in kwargs.keys():
            if kwarg in result.keys() and result[kwarg] == kwargs[kwarg]:
                continue
            else:
                match = False

        if match:
            return Some(result)

    return Nothing()


def get_fcp_config(name: str) -> str:
    config_dir = os.path.join(THIS_DIR, "schemas")
    return os.path.join(config_dir, name + ".fcp")


@pytest.mark.parametrize("test_name", ["001_basic_struct", "002_nested_enum", "003_simple_array", "004_enum_array"])  # type: ignore
def test_codegen(test_name: str) -> None:
    with tempfile.TemporaryDirectory() as tempdirname:
        print(tempdirname, type(tempdirname))

        fcp_v2, _ = get_fcp(Path(get_fcp_config(test_name))).unwrap()

        generator = Generator()

        results = generator.generate(fcp_v2, {"output": tempdirname})

        for result in results:
            handle_result(result)

        shutil.copyfile(
            Path(THIS_DIR) / f"{test_name}.cpp",
            Path(tempdirname) / f"{test_name}.cpp",
        )

        shutil.copyfile(
            Path(THIS_DIR) / "utest.h",
            Path(tempdirname) / "utest.h",
        )

        out = subprocess.run(
            [
                "/usr/bin/g++",
                f"{test_name}.cpp",
                "-o",
                test_name,
            ],
            cwd=tempdirname,
            capture_output=True,
        )
        print(out.stderr.decode("utf-8"))
        assert out.returncode == 0

        out = subprocess.run(["./" + test_name], cwd=tempdirname, capture_output=True)
        print(out.stdout.decode("utf-8"))
        assert out.returncode == 0
