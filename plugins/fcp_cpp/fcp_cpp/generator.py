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

from beartype.typing import Any, Dict, Union, List
from typing_extensions import NoReturn
from pathlib import Path
import jinja2
import math
import os

from fcp.specs.type import Type
from fcp.specs.impl import Impl
from fcp.codegen import CodeGenerator
from fcp.verifier import Verifier
from fcp.specs.v2 import FcpV2
from fcp.specs.type import (
    BuiltinType,
    ArrayType,
    ComposedTypeCategory,
    ComposedType,
    DynamicArrayType,
    OptionalType,
)
from fcp.encoding import make_encoder, EncodeablePiece, EncoderContext, Value


def _to_highest_power_of_two(n: int) -> int:
    return int(max(2 ** math.ceil(math.log2(n)), 8))


def to_wrapper_cpp_type(input: Type) -> str:
    """Convert fcp type to wrapper C++ type."""
    if isinstance(input, BuiltinType):
        if input.is_unsigned():
            size = input.get_length()
            cpp_size = _to_highest_power_of_two(size)
            return f"Unsigned<std::uint{cpp_size}_t, {size}>"
        elif input.is_signed():
            size = input.get_length()
            cpp_size = _to_highest_power_of_two(size)
            return f"Signed<std::int{cpp_size}_t, {size}>"
        elif input.is_float():
            return "Float"
        elif input.is_double():
            return "Double"
        elif input.is_str():
            return "String"
    elif isinstance(input, ArrayType):
        underlying_type = to_wrapper_cpp_type(input.underlying_type)
        return f"Array<{underlying_type}, {input.size}>"
    elif isinstance(input, ComposedType):
        if input.type == ComposedTypeCategory.Struct:
            return str(input.name)
        elif input.type == ComposedTypeCategory.Enum:
            return str(input.name)
    elif isinstance(input, DynamicArrayType):
        underlying_type = to_wrapper_cpp_type(input.underlying_type)
        return f"DynamicArray<{underlying_type}>"
    elif isinstance(input, OptionalType):
        underlying_type = to_wrapper_cpp_type(input.underlying_type)
        return f"Optional<{underlying_type}>"

    raise ValueError("Cannot convert type to C++ type")


class CanEncoding:
    """Can encoding representation used in templates."""

    def __init__(self, impl: Impl, encoding: List[EncodeablePiece]) -> None:
        self.impl = impl
        self.encoding = encoding
        self.id = impl.fields.get("id")
        self.device_name = impl.fields.get("device")
        self.dlc = math.ceil((encoding[-1].bitstart + encoding[-1].bitlength) / 8)


class Generator(CodeGenerator):
    """Cpp code generator."""

    def __init__(self) -> None:
        pass

    def _fcp_header(self) -> str:
        return (
            (Path(os.path.dirname(os.path.abspath(__file__))) / "fcp.h.j2")
            .open()
            .read()
        )

    def _can_header(self) -> str:
        return (
            (Path(os.path.dirname(os.path.abspath(__file__))) / "fcp_can.h.j2")
            .open()
            .read()
        )

    def _buffer_header(self) -> str:
        return (
            (Path(os.path.dirname(os.path.abspath(__file__))) / "buffer.h.j2")
            .open()
            .read()
        )

    def _decoders_header(self) -> str:
        return (
            (Path(os.path.dirname(os.path.abspath(__file__))) / "decoders.h.j2")
            .open()
            .read()
        )

    def _dynamic_header(self) -> str:
        return (
            (Path(os.path.dirname(os.path.abspath(__file__))) / "dynamic.h.j2")
            .open()
            .read()
        )

    def generate(self, fcp: FcpV2, ctx: Any) -> Dict[str, Union[str, Path]]:
        """Generate cpp files."""
        loader = jinja2.DictLoader(
            {
                "fcp_header": self._fcp_header(),
                "can_header": self._can_header(),
                "buffer_header": self._buffer_header(),
                "decoders_header": self._decoders_header(),
                "dynamic_header": self._dynamic_header(),
            }
        )

        env = jinja2.Environment(loader=loader)
        env.globals["to_wrapper_cpp_type"] = to_wrapper_cpp_type

        return [
            {
                "type": "file",
                "path": Path(ctx.get("output")) / "fcp.h",
                "contents": env.get_template("fcp_header").render(
                    {"fcp": fcp, "structs": fcp.structs}
                ),
            },
            {
                "type": "file",
                "path": Path(ctx.get("output")) / "buffer.h",
                "contents": env.get_template("buffer_header").render(),
            },
            {
                "type": "file",
                "path": Path(ctx.get("output")) / "decoders.h",
                "contents": env.get_template("decoders_header").render(),
            },
            {
                "type": "file",
                "path": Path(ctx.get("output")) / "dynamic.h",
                "contents": env.get_template("dynamic_header").render(),
            },
            # {
            #    "type": "file",
            #    "path": Path(ctx.get("output")) / "fcp_can.h",
            #    "contents": env.get_template("can_header").render(
            #        {"fcp": fcp, "can_encodings": can_encodings, "structs": structs}
            #    ),
            # },
        ]

    def register_checks(self, verifier: Verifier) -> NoReturn:  # type: ignore
        """Register cpp specific checks."""
        pass
