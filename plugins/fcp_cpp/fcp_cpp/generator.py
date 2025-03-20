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
    BuiltinType,
    ArrayType,
    ComposedTypeCategory,
    ComposedType,
    DynamicArrayType,
    OptionalType,
)
from fcp.specs.struct_field import StructField
from fcp.specs.metadata import MetaData
from fcp.specs.enum import Enum, Enumeration
from fcp.version import VERSION
from fcp.reflection import get_reflection_schema


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


def create_template_environment(output):
    def get_template(self, filename: str) -> str:
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
    def __init__(self, metadata):
        self.metadata = metadata
        self.output = []

    def with_file(self, filename, template_name, template_arguments={}):
        self.output.append((filename, template_name, template_arguments | metadata))


class Generator(CodeGenerator):
    """Cpp code generator."""

    def __init__(self) -> None:
        self.service_methods_enum = {}
        pass

    def create_rpc_input_data(self, service, payload: Struct) -> Struct:
        payload_type_name = payload.name + "Input"
        s = Struct(
            name=payload_type_name,
            fields=[
                StructField(
                    name="service_id",
                    field_id=0,
                    type=ComposedType("ServiceId", ComposedTypeCategory.Enum),
                ),
                StructField(
                    name="method_id",
                    field_id=1,
                    type=ComposedType(
                        service.name + "MethodId", ComposedTypeCategory.Enum
                    ),
                ),
                StructField(
                    name="payload",
                    field_id=2,
                    type=ComposedType(payload.name, ComposedTypeCategory.Struct),
                ),
            ],
        )
        i = Impl(
            name=payload_type_name,
            protocol="default",
            type=payload_type_name,
            fields={},
            signals=[],
            meta=MetaData(0, 0, 0, 0, 0, 0, ""),
        )
        i._is_method_input = True
        return (s, i)

    def create_rpc_output_data(self, service, payload: Struct) -> Struct:
        payload_type_name = payload.name + "Output"
        s = Struct(
            name=payload_type_name,
            fields=[
                StructField(
                    name="service_id",
                    field_id=0,
                    type=ComposedType("ServiceId", ComposedTypeCategory.Enum),
                ),
                StructField(
                    name="method_id",
                    field_id=1,
                    type=ComposedType(
                        service.name + "MethodId", ComposedTypeCategory.Enum
                    ),
                ),
                StructField(
                    name="payload",
                    field_id=2,
                    type=ComposedType(payload.name, ComposedTypeCategory.Struct),
                ),
            ],
        )
        i = Impl(
            name=payload_type_name,
            protocol="default",
            type=payload_type_name,
            fields={},
            signals=[],
            meta=None,
        )
        return (s, i)

    def generate(self, fcp: FcpV2, ctx: Any) -> List[Dict[str, Union[str, Path]]]:
        """Generate cpp files."""
        fcp_reflection, _ = get_reflection_schema().unwrap()

        metadata = {
            "version": VERSION,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user": pwd.getpwuid(os.getuid())[0],
            "hostname": socket.gethostname(),
        }
        method_inputs = {}
        method_outputs = {}

        for service in fcp.services:
            self.service_methods_enum[service.name] = []
            for method in service.methods:
                input_struct = fcp.get_struct(method.input).unwrap()
                output_struct = fcp.get_struct(method.output).unwrap()
                input_struct = fcp.get_struct(method.input).unwrap()
                method_inputs[method.input] = self.create_rpc_input_data(
                    service, input_struct
                )
                output_struct = fcp.get_struct(method.output).unwrap()
                method_outputs[method.output] = self.create_rpc_output_data(
                    service, output_struct
                )
                self.service_methods_enum[service.name].append((method.name, method.id))

        for rpc_input_struct, rpc_input_impl in method_inputs.values():
            fcp.structs.append(rpc_input_struct)
            fcp.impls.append(rpc_input_impl)

        for rpc_output_struct, rpc_output_impl in method_outputs.values():
            fcp.structs.append(rpc_output_struct)
            fcp.impls.append(rpc_output_impl)

        service_id = Enum(
            name="ServiceId",
            enumeration=[
                Enumeration(service.name, service.id, None) for service in fcp.services
            ],
            meta=None,
        )
        m = max([e.value for e in service_id.enumeration])
        if m > 255:
            raise ValueError("ServiceId must not be larger than 8 bit")
        elif m != 255:
            service_id.enumeration.append(Enumeration("Max", 255, None))

        fcp.enums.append(service_id)

        for service_name, service_method_enum in self.service_methods_enum.items():
            enum = Enum(
                name=service_name + "MethodId",
                enumeration=[
                    Enumeration(method_name, id, None)
                    for method_name, id in service_method_enum
                ],
                meta=None,
            )
            m = max([e.value for e in enum.enumeration])
            if m > 255:
                raise ValueError(
                    service_name + "MethodId must not be larger than 8 bit"
                )
            elif m != 255:
                enum.enumeration.append(Enumeration("Max", 255, None))

            fcp.enums.append(enum)

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
        output_builder.with_file("can_static_schema.h", "can_static_schema.h")
        output_builder.with_file("can_dynamic_schema.h", "can_dynamic_schema.h")
        output_builder.with_file("i_schema.h", "i_schema.h")
        output_builder.with_file("rpc.h", "rpc.h", {"fcp": fcp})

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
