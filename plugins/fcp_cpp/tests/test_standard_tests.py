import os
import json
from pathlib import Path

THIS_DIR = Path(os.path.dirname(os.path.abspath(__file__)))


def to_constant(value):
    if isinstance(value, str):
        return f'"{value}"'
    return str(value)


def test_standarized_tests():
    standardized = THIS_DIR.parent.parent.parent / "tests" / "standardized"

    with (standardized / "fcp_tests.json").open() as f:
        standardized_tests = json.loads(f.read())

    print('#include "fcp.h"')
    print('#include "utest.h"')
    print("UTEST_MAIN()")

    for suite in standardized_tests:
        with (standardized / suite["schema"]).open() as f:
            fcp_schema = f.read()

        for test in suite["tests"]:
            print(
                "UTEST(",
                suite["name"],
                ",",
                "Encode" + test["name"].capitalize(),
                ") {",
            )

            args = ",".join(
                [to_constant(value["value"]) for _, value in test["decoded"].items()]
            )
            print("\tauto x =", "fcp::" + test["datatype"] + "{" + args + "};")
            print("\tauto encoded = x.encode().GetData();")
            print(
                "\tstd::vector<std::uint8_t> expected = {"
                + ",".join([to_constant(x) for x in test["encoded"]["value"]])
                + "};"
            )

            print("\tEXPECT_TRUE(encoded == expected);")
            print("}")

    assert False
