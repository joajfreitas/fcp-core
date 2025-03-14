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

"""Generation of rpc types."""

from fcp.specs.v2 import FcpV2
from fcp.specs.struct import Struct, StructField
from fcp.specs.type import BuiltinType, ComposedType, ComposedTypeCategory
from fcp.specs.impl import Impl
from fcp.specs.metadata import MetaData


def _create_rpc_input_data(service: Service, payload: Struct) -> Struct:
    payload_type_name = payload.name + "Input"
    return (
        Struct(
            name=payload_type_name,
            fields=[
                StructField(name="service_id", field_id=0, type=BuiltinType("u8")),
                StructField(name="method_id", field_id=1, type=BuiltinType("u8")),
                StructField(
                    name="payload",
                    field_id=2,
                    type=ComposedType(payload.name, ComposedTypeCategory.Struct),
                ),
            ],
        ),
        Impl(
            name=payload_type_name,
            protocol="default",
            type=payload_type_name,
            fields={},
            signals=[],
            meta=MetaData(0, 0, 0, 0, 0, 0, ""),
        ),
    )


def _create_rpc_output_data(self, service: Service, payload: Struct) -> Struct:
    payload_type_name = payload.name + "Output"
    return (
        Struct(
            name=payload_type_name,
            fields=[
                StructField(name="service_id", field_id=0, type=BuiltinType("u8")),
                StructField(name="method_id", field_id=1, type=BuiltinType("u8")),
                StructField(
                    name="payload",
                    field_id=2,
                    type=ComposedType(payload.name, ComposedTypeCategory.Struct),
                ),
            ],
        ),
        Impl(
            name=payload_type_name,
            protocol="default",
            type=payload_type_name,
            fields={},
            signals=[],
            meta=MetaData(0, 0, 0, 0, 0, 0, ""),
        ),
    )


def generate_rpc(
    fcp: FcpV2,
) -> FcpV2:

    method_inputs = {}
    method_outputs = {}

    service_methods_enum = {}

    for service in fcp.services:
        for method in service.methods:
            input_struct = fcp.get_struct(method.input).unwrap()
            output_struct = fcp.get_struct(method.output).unwrap()
            method_inputs.add(method.input)
            method_outputs.add(method.output)

    for method_input in method_inputs:
        input_struct = fcp.get_struct(method_input).unwrap()
        rpc_input_struct, rpc_input_impl = create_rpc_input_data(input_struct)
        fcp.structs.append(rpc_input_struct)
        fcp.impls.append(rpc_input_impl)

    for method_output in method_outputs:
        output_struct = fcp.get_struct(method_output).unwrap()
        rpc_output_struct, rpc_output_impl = create_rpc_output_data(output_struct)
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

    for service_name, service_method_enum in service_methods_enum.items():
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
            raise ValueError(service_name + "MethodId must not be larger than 8 bit")
        elif m != 255:
            enum.enumeration.append(Enumeration("Max", 255, None))

        fcp.enums.append(enum)

        return fcp
