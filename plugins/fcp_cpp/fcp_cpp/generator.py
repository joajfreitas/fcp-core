from beartype.typing import Any, Dict, Union
from typing_extensions import NoReturn
from pathlib import Path
import jinja2
import math

from fcp.codegen import CodeGenerator
from fcp.verifier import Verifier
from fcp import FcpV2
from fcp.specs.type import BuiltinType


def to_cpp_type(input):
    def to_highest_power_of_two(n):
        return 2 ** math.ceil(math.log2(n))

    if isinstance(input, BuiltinType):
        prefix = input.name[0]
        bits = int(input.name[1:])

        bits = to_highest_power_of_two(bits)

        if prefix == "u" or prefix == "i":
            return prefix + "int" + str(bits) + "_t"
        elif prefix == "f" and bits == 32:
            return "float"
        elif prefix == "f" and bits == 64:
            return "double"
        else:
            raise ValueError(f"Not a valid builtin type: {input}")
    else:
        return input.name


class Generator(CodeGenerator):
    def __init__(self) -> None:
        pass

    def header(self):
        return """
#ifndef __HEADER__
#define __HEADER__

{% for enum in fcp.enums -%}
enum {{enum.name}} {
    {% for enumeration in enum.enumeration -%}
    {{enumeration.name}} = {{enumeration.value}},
    {% endfor %}
};

{% endfor -%}

{% for struct in fcp.structs -%}
struct {{struct.name}} {
    {% for signal in struct.fields -%}
    {{signal.type | to_cpp_type}} {{signal.name}};
    {% endfor %}
};

{% endfor -%}

#endif
"""

    def generate(self, fcp: FcpV2, ctx: Any) -> Dict[str, Union[str, Path]]:
        loader = jinja2.DictLoader({"header": self.header()})

        env = jinja2.Environment(autoescape=True, loader=loader)
        env.filters["to_cpp_type"] = to_cpp_type
        
        print(env.get_template("header").render({"fcp": fcp}))

        return []

    def register_checks(self, verifier: Verifier) -> NoReturn:
        pass
