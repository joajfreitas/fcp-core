"""Cpp generator."""

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

from beartype.typing import Any, Dict, Union
from typing_extensions import NoReturn
from pathlib import Path
import jinja2
import math

from fcp.specs.type import Type
from fcp.codegen import CodeGenerator
from fcp.verifier import Verifier
from fcp import FcpV2
from fcp.specs.type import BuiltinType


def to_cpp_type(input: Type) -> str:
    """Convert fcp type to cpp type."""

    def to_highest_power_of_two(n: int) -> int:
        return int(2 ** math.ceil(math.log2(n)))

    if isinstance(input, BuiltinType):
        prefix = input.name[0]
        bits = int(input.name[1:])

        bits = to_highest_power_of_two(bits)

        if prefix == "u" or prefix == "i":
            return str(prefix + "int" + str(bits) + "_t")
        elif prefix == "f" and bits == 32:
            return "float"
        elif prefix == "f" and bits == 64:
            return "double"
        else:
            raise ValueError(f"Not a valid builtin type: {input}")
    else:
        return str(input.name)


class Generator(CodeGenerator):
    """Cpp code generator."""

    def __init__(self) -> None:
        pass

    def _header(self) -> str:
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
        """Generate cpp files."""
        loader = jinja2.DictLoader({"header": self._header()})

        env = jinja2.Environment(autoescape=True, loader=loader)
        env.filters["to_cpp_type"] = to_cpp_type

        print(env.get_template("header").render({"fcp": fcp}))

        return []

    def register_checks(self, verifier: Verifier) -> NoReturn:  # type: ignore
        """Register cpp specific checks."""
        pass
