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

"""Cpp generator."""

from beartype.typing import Any, Dict, Union, List, Tuple
from typing_extensions import NoReturn
from pathlib import Path
import jinja2
import math
import os
import pwd
import socket
import datetime

from fcp.utils import to_pascal_case, to_snake_case
from fcp.specs.impl import Impl
from fcp.codegen import CodeGenerator
from fcp.verifier import Verifier
from fcp.specs.v2 import FcpV2
from fcp.specs.struct import Struct
from fcp.specs.type import Type, StructType
from fcp.specs import type
from fcp.version import VERSION
from fcp.type_visitor import TypeVisitor
from fcp.reflection import get_reflection_schema

from .rpc import generate_rpc


def _to_highest_power_of_two(n: int) -> int:
    return int(max(2 ** math.ceil(math.log2(n)), 8))


class ToCpp(TypeVisitor):
    """Fcp type to cpp conversion."""

    def struct(self, t: type.StructType, fields: List[type.Type]) -> str:
        """Convert struct to cpp."""
        return str(t.name)

    def enum(self, t: type.EnumType) -> str:
        """Convert enum to cpp."""
        return str(t.name)

    def unsigned(self, t: type.UnsignedType) -> str:
        """Convert unsigned to cpp."""
        size = t.get_length()
        cpp_size = _to_highest_power_of_two(size)
        return f"Unsigned<std::uint{cpp_size}_t, {size}>"

    def signed(self, t: type.SignedType) -> str:
        """Convert signed to cpp."""
        size = t.get_length()
        cpp_size = _to_highest_power_of_two(size)
        return f"Signed<std::int{cpp_size}_t, {size}>"

    def float(self, t: type.FloatType) -> str:
        """Convert float to cpp."""
        return "Float"

    def double(self, t: type.DoubleType) -> str:
        """Convert double to cpp."""
        return "Double"

    def string(self, t: type.StringType) -> str:
        """Convert string to cpp."""
        return "String"

    def array(self, t: type.ArrayType, inner: type.Type) -> str:
        """Convert array to cpp."""
        return f"Array<{inner}, {t.size}>"

    def dynamic_array(self, t: type.DynamicArrayType, inner: type.Type) -> str:
        """Convert dynamic array to cpp."""
        return f"DynamicArray<{inner}>"

    def optional(self, t: type.OptionalType, inner: type.Type) -> str:
        """Convert optional to cpp."""
        return f"Optional<{inner}>"


def to_wrapper_cpp_type(fcp: FcpV2, input: Type) -> str:
    """Convert fcp type to wrapper C++ type."""
    return str(ToCpp(fcp).visit(input))


def get_matching_impls(fcp: FcpV2, protocol: str) -> List[Impl]:
    """Get impls matching a protocol."""
    return fcp.get_matching_impls_or_default(protocol)


def get_struct_from_type(fcp: FcpV2, type: str) -> Struct:
    """Get struct from type name."""
    return fcp.get_type(StructType(type)).unwrap()


def create_template_environment(
    output: List[Tuple[str, str, Dict[str, Any]]],
) -> jinja2.Environment:
    """Create jinja2 template environment."""

    def get_template(filename: str) -> str:
        return (
            (Path(os.path.dirname(os.path.abspath(__file__))) / filename).open().read()
        )

    loader = jinja2.DictLoader(
        {
            template_name: get_template(template_name)
            for template_name in set([template_name for _, template_name, _ in output])
        }
    )

    env = jinja2.Environment(loader=loader)
    env.globals["to_wrapper_cpp_type"] = to_wrapper_cpp_type
    env.globals["get_matching_impls"] = get_matching_impls
    env.globals["get_struct_from_type"] = get_struct_from_type
    env.filters["to_pascal_case"] = to_pascal_case

    return env


class OutputBuilder:
    """Builder for output file list."""

    def __init__(self, metadata: Dict[str, str]) -> None:
        self.metadata = metadata
        self.output: List[Tuple[str, str, Dict[str, Any]]] = []

    def with_file(
        self, filename: str, template_name: str, template_arguments: Dict[str, Any] = {}
    ) -> None:
        """Add file to output list."""
        self.output.append(
            (filename, template_name, {**template_arguments, **self.metadata})
        )


class Generator(CodeGenerator):
    """Cpp code generator."""

    def __init__(self) -> None:
        pass

    def generate(self, fcp: FcpV2, ctx: Any) -> List[Dict[str, Union[str, Path]]]:
        """Generate cpp files."""
        fcp_reflection = get_reflection_schema().unwrap()
        fcp = generate_rpc(fcp)

        output_builder = OutputBuilder(
            {
                "version": VERSION,
                "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "user": pwd.getpwuid(os.getuid())[0],
                "hostname": socket.gethostname(),
            }
        )

        output_builder.with_file(
            "fcp.h", "fcp.h.j2", {"fcp": fcp, "namespace": None, "protocol": "default"}
        )
        output_builder.with_file("buffer.h", "buffer.h")
        output_builder.with_file("decoders.h", "decoders.h")
        output_builder.with_file("dynamic.h", "dynamic.h")
        output_builder.with_file(
            "reflection.h",
            "fcp.h.j2",
            {"fcp": fcp_reflection, "namespace": "reflection", "protocol": "default"},
        )

        output_builder.with_file("can.h", "can.h", {"fcp": fcp})
        output_builder.with_file("i_can_schema.h", "i_can_schema.h")
        output_builder.with_file(
            "can_static_schema.h", "can_static_schema.h", {"fcp": fcp}
        )
        output_builder.with_file("can_dynamic_schema.h", "can_dynamic_schema.h")
        output_builder.with_file("i_schema.h", "i_schema.h")
        output_builder.with_file("rpc.h", "rpc.h.j2", {"fcp": fcp})

        for protocol in fcp.get_protocols():
            output_builder.with_file(
                "fcp_" + protocol + ".h",
                "fcp.h.j2",
                {"fcp": fcp, "namespace": protocol, "protocol": protocol},
            )

        for service in fcp.services:
            output_builder.with_file(
                to_snake_case(service.name) + "_server.h",
                "service_server.h.j2",
                {"fcp": fcp, "service": service},
            )
            output_builder.with_file(
                to_snake_case(service.name) + "_client.h",
                "service_client.h.j2",
                {"fcp": fcp, "service": service},
            )

        env = create_template_environment(output_builder.output)

        return [
            {
                "type": "file",
                "path": Path(ctx.get("output")) / output_file,
                "contents": env.get_template(template_name).render(template_arguments),
            }
            for output_file, template_name, template_arguments in output_builder.output
        ]

    def register_checks(self, verifier: Verifier) -> NoReturn:  # type: ignore
        """Register cpp specific checks."""
        pass
