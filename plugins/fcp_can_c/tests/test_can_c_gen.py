import pytest
import os
import subprocess
from pathlib import Path
from fcp_can_c import Generator
from fcp.v2_parser import get_fcp


base_dir = os.getcwd().split("/")[-1]


def get_fcp_config(test_dir: str, name: str) -> str:
    config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), test_dir)
    return os.path.join(config_dir, "test.fcp")


def get_path(test_name: str) -> str:
    if base_dir == "fcp_can_c":
        return f"tests/{test_name}"
    elif base_dir == "fcp-core":
        return f"plugins/fcp_can_c/tests/{test_name}"
    else:
        raise ValueError(f"Invalid testsinvocation directory: {base_dir}")


@pytest.mark.parametrize(
    "test_name",
    [
        "001_basic_struct",
        "002_nested_enum",
        "003_msg_scheduling",
    ],
)
def test_can_c_gen(test_name: str):
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
