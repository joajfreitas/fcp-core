# ruff: noqa: D103 D100

import pytest
import os
import subprocess
from pathlib import Path
from fcp_can_c import Generator
from fcp.v2_parser import get_fcp


base_dir = os.path.abspath(__file__).replace("/test_can_c_gen.py", "")
cwd = os.getcwd().split("/")[-1]


def get_path(test_name: str) -> str:
    return f"{base_dir}/{test_name}"


@pytest.mark.parametrize(
    "test_name",
    [
        "001_basic_struct",
        "002_nested_enum",
        "003_msg_scheduling",
    ],
)  # type: ignore
def test_can_c_gen(test_name: str) -> None:
    fcp_v2, _ = get_fcp(Path(get_path(test_name) + "/test.fcp")).unwrap()
    generator = Generator()

    # Use test_name in the output path for generated files
    output_path = get_path(test_name) + "/generated_code"
    results = generator.gen(fcp_v2, None, None, os.path.join("tests", output_path))

    # List contents of the directory before running make
    for root, dirs, files in os.walk(output_path):
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
