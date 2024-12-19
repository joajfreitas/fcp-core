import os
import json5
import jinja2
from pathlib import Path
import tempfile
import shutil
import subprocess

from fcp.codegen import handle_result
from fcp_cpp import Generator
from fcp.v2_parser import get_fcp

THIS_DIR = Path(os.path.dirname(os.path.abspath(__file__)))


def to_constant(value):
    if value["type"] == "str":
        return f'"{value["value"]}"'
    elif value["type"] in ["u8", "u16", "u32", "u64", "i8", "i16", "i32", "f32", "f64"]:
        return str(value["value"])
    elif value["type"] == "u64":
        return str(value["value"]) + "ULL"
    elif value["type"] == "i64":
        return str(value["value"]) + "LL"
    elif value["type"] == "enum":
        return "fcp::" + value["enum"] + "::" + value["value"]
    elif value["type"] == "array":
        return "{" + ",".join([to_constant({"type": value["subtype"], "value": v}) for v in value["value"]]) + "}"

    raise ValueError(f"Unknown type: {value['type']}")


def get_fcp_config(name: str) -> str:
    config_dir = os.path.join(THIS_DIR, "schemas")
    return os.path.join(config_dir, name + ".fcp")


def to_cpp_initializer_list(values):
    initializers = []

    for value in values:
        initializers.append(to_constant(value))

    return "{" + ",".join(initializers) + "}"


test_template = """
#include "fcp.h"
#include "utest.h"

UTEST_MAIN()

{% for suite in standardized_tests %}
{% for test in suite["tests"] %}
UTEST({{ suite["name"] }}, {{ test["name"] }}) {
    auto x = fcp::{{test["datatype"]}} {{ to_cpp_initializer_list(test["decoded"]) }};

    auto encoded = x.encode().GetData();

    std::vector<std::uint8_t> expected { {%- for value in test["encoded"]["value"] -%} {{value}} {%- if not loop.last -%},{%- endif -%}{%- endfor -%} };

    EXPECT_TRUE(encoded == expected);
}
{% endfor %}
{% endfor %}
"""


def test_standardized_tests():
    standardized = THIS_DIR.parent.parent.parent / "tests" / "standardized"

    with (standardized / "fcp_tests.json").open() as f:
        standardized_tests = json5.loads(f.read())

    loader = jinja2.DictLoader(
        {
            "test_template": test_template
        }
    )

    env = jinja2.Environment(loader=loader)
    env.globals["to_cpp_initializer_list"] = to_cpp_initializer_list
    template = env.get_template("test_template")
    
    template_data = []

    for suite in standardized_tests:
        test_suite = {
            "name": suite["name"],
            "schema": suite["schema"]
            "tests": []
        }
        for test in suite["tests"]:
            template_data.append(
                {
                    "suite": suite["name"],
                    "test": test["name"],
                    "datatype": test["datatype"],
                    "decoded": test["decoded"],
                    "encoded": test["encoded"],
                }
            )

    template_data.append(test_suite)

    suite = standardized_tests[0]
    test = suite["tests"][0]
    file = template.render(
        {
            "standardized_tests": standardized_tests,
            "suite_name": "Suite",
            "test_name": "Test",
            "datatype": "S1",
            "test": test,
        }
    )

    print(file)
    with tempfile.TemporaryDirectory() as tempdirname:
        tempdir = Path(tempdirname)

        with open(tempdir / "test.cpp", "w") as f:
            f.write(file)

        fcp_v2, _ = get_fcp(
            "/home/joaj/sources/fcp-core/tests/standardized/001_basic_values.fcp"
        ).unwrap()
        generator = Generator()
        results = generator.generate(fcp_v2, {"output": tempdirname})

        for result in results:
            handle_result(result)

        shutil.copyfile(
            Path(THIS_DIR) / "utest.h",
            Path(tempdirname) / "utest.h",
        )

        out = subprocess.run(
            [
                "/usr/bin/g++",
                "--std=c++17",
                f"test.cpp",
                "-o",
                "test",
            ],
            cwd=tempdirname,
            capture_output=True,
        )
        print(out.stderr.decode("utf-8"))
        assert out.returncode == 0

        out = subprocess.run(["./test"], cwd=tempdirname, capture_output=True)
        print(out.stdout.decode("utf-8"))
        assert out.returncode == 0
