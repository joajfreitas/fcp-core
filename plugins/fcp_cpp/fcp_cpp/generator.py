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

from beartype.typing import Any, Dict, Union, List
from typing_extensions import NoReturn
from pathlib import Path
import jinja2
import math
import os
import pwd
import socket
import datetime

from fcp.specs.impl import Impl
from fcp.codegen import CodeGenerator
from fcp.verifier import Verifier
from fcp.specs.v2 import FcpV2
from fcp.specs.struct import Struct
from fcp.specs.type import (
    Type,
    ComposedTypeCategory,
    ComposedType,
)
from fcp.specs import type
from fcp.version import VERSION
from fcp.type_visitor import TypeVisitor
from fcp.reflection import get_reflection_schema


def _to_highest_power_of_two(n: int) -> int:
    return int(max(2 ** math.ceil(math.log2(n)), 8))


class ToCpp(TypeVisitor):
    """Fcp type to cpp convertion."""

    def struct(self, t: type.ComposedType, fields: List[type.Type]) -> str:
        """Convert struct to cpp."""
        return str(t.name)

    def enum(self, t: type.ComposedType) -> str:
        """Convert enum to cpp."""
        return str(t.name)

    def unsigned(self, t: type.BuiltinType) -> str:
        """Convert unsigned to cpp."""
        size = t.get_length()
        cpp_size = _to_highest_power_of_two(size)
        return f"Unsigned<std::uint{cpp_size}_t, {size}>"

    def signed(self, t: type.BuiltinType) -> str:
        """Convert signed to cpp."""
        size = t.get_length()
        cpp_size = _to_highest_power_of_two(size)
        return f"Signed<std::int{cpp_size}_t, {size}>"

    def float(self, t: type.BuiltinType) -> str:
        """Convert float to cpp."""
        return "Float"

    def double(self, t: type.BuiltinType) -> str:
        """Convert double to cpp."""
        return "Double"

    def string(self, t: type.BuiltinType) -> str:
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
    return fcp.get_type(ComposedType(type, ComposedTypeCategory.Struct)).unwrap()


def to_pascal_case(name: str) -> str:
    """Convert snake case to pascal case."""
    return "".join([n.capitalize() for n in name.split("_")])


def to_snake_case(name: str) -> str:
    """Convert pascal case to snake case."""
    return name[:1].lower() + "".join(
        "_" + c.lower() if c.isupper() else c for c in name[1:]
    )


class Generator(CodeGenerator):
    """Cpp code generator."""

    def __init__(self) -> None:
        pass

    def _get_template(self, filename: str) -> str:
        return (
            (Path(os.path.dirname(os.path.abspath(__file__))) / filename).open().read()
        )

    def generate(self, fcp: FcpV2, ctx: Any) -> List[Dict[str, Union[str, Path]]]:
        """Generate cpp files."""
        fcp_reflection, _ = get_reflection_schema().unwrap()

        metadata = {
            "version": VERSION,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user": pwd.getpwuid(os.getuid())[0],
            "hostname": socket.gethostname(),
        }
        output_files = (
            [
                (
                    "fcp.h.j2",
                    "fcp.h",
                    {
                        "fcp": fcp,
                        "namespace": None,
                        "protocol": "default",
                        **metadata,
                    },
                ),
                ("buffer.h", "buffer.h", {**metadata}),
                ("decoders.h", "decoders.h", {**metadata}),
                ("dynamic.h", "dynamic.h", {**metadata}),
                (
                    "fcp.h.j2",
                    "reflection.h",
                    {
                        **metadata,
                        "fcp": fcp_reflection,
                        "namespace": "reflection",
                        "protocol": "default",
                    },
                ),
                (
                    "can.h",
                    "can.h",
                    {
                        **metadata,
                        "fcp": fcp,
                    },
                ),
                ("i_can_schema.h", "i_can_schema.h", {**metadata}),
                (
                    "can_static_schema.h",
                    "can_static_schema.h",
                    {**metadata, "fcp": fcp},
                ),
                ("can_dynamic_schema.h", "can_dynamic_schema.h", {**metadata}),
                ("i_schema.h", "i_schema.h", {**metadata}),
                (
                    "rpc.h.j2",
                    "rpc.h",
                    {**metadata, "fcp": fcp},
                ),
            ]
            + [
                (
                    "fcp.h.j2",
                    "fcp_" + protocol + ".h",
                    {
                        **metadata,
                        "fcp": fcp,
                        "namespace": protocol,
                        "protocol": protocol,
                    },
                )
                for protocol in fcp.get_protocols()
            ]
            + [
                (
                    "service_server.h.j2",
                    to_snake_case(service.name) + "_server.h",
                    {**metadata, "fcp": fcp, "service": service},
                )
                for service in fcp.services
            ]
            + [
                (
                    "service_client.h.j2",
                    to_snake_case(service.name) + "_client.h",
                    {**metadata, "fcp": fcp, "service": service},
                )
                for service in fcp.services
            ]
        )

        loader = jinja2.DictLoader(
            {
                template_name: self._get_template(template_name)
                for template_name in set(
                    [template_name for template_name, _, _ in output_files]
                )
            }
        )

        env = jinja2.Environment(loader=loader)
        env.globals["to_wrapper_cpp_type"] = to_wrapper_cpp_type
        env.globals["get_matching_impls"] = get_matching_impls
        env.globals["get_struct_from_type"] = get_struct_from_type
        env.filters["to_pascal_case"] = to_pascal_case

        return [
            {
                "type": "file",
                "path": Path(ctx.get("output")) / output_file,
                "contents": env.get_template(template_name).render(template_arguments),
            }
            for template_name, output_file, template_arguments in output_files
        ]

    def register_checks(self, verifier: Verifier) -> NoReturn:  # type: ignore
        """Register cpp specific checks."""
        pass
