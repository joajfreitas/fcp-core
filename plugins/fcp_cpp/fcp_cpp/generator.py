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
from fcp import FcpV2
from fcp.specs.type import BuiltinType
from fcp.encoding import make_encoder, EncodeablePiece


def to_cpp_type(input: Type) -> str:
    """Convert fcp type to cpp type."""

    def _to_highest_power_of_two(n: int) -> int:
        return int(max(2 ** math.ceil(math.log2(n)), 8))

    if isinstance(input, BuiltinType):
        prefix = input.name[0]
        bits = int(input.name[1:])

        bits = _to_highest_power_of_two(bits)

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

    # TODO: generate to string
    def generate(self, fcp: FcpV2, ctx: Any) -> Dict[str, Union[str, Path]]:
        """Generate cpp files."""
        loader = jinja2.DictLoader(
            {
                "fcp_header": self._fcp_header(),
                "can_header": self._can_header(),
            }
        )

        env = jinja2.Environment(autoescape=True, loader=loader)
        env.filters["to_cpp_type"] = to_cpp_type

        encoder = make_encoder("packed", fcp)
        can_encodings = {}

        for impl in fcp.get_matching_impls("can"):
            encoding = encoder.generate(impl)
            for encode_piece in encoding:
                encode_piece.name = encode_piece.name.replace("::", ".")

            can_encodings[impl.type] = CanEncoding(impl, encoding)

        structs = [(struct, can_encodings.get(struct.name)) for struct in fcp.structs]

        return [
            {
                "type": "file",
                "path": Path(ctx.get("output")) / "fcp.h",
                "contents": env.get_template("fcp_header").render(
                    {"fcp": fcp, "can_encodings": can_encodings, "structs": structs}
                ),
            },
            {
                "type": "file",
                "path": Path(ctx.get("output")) / "fcp_can.h",
                "contents": env.get_template("can_header").render(
                    {"fcp": fcp, "can_encodings": can_encodings, "structs": structs}
                ),
            },
        ]

    def register_checks(self, verifier: Verifier) -> NoReturn:  # type: ignore
        """Register cpp specific checks."""
        pass
