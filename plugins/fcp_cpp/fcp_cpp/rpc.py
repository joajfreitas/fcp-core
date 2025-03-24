# Copyright (c) 2025 the fcp AUTHORS.
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

import math
from beartype.typing import Tuple, Dict

from fcp.specs.v2 import FcpV2
from fcp.specs.impl import Impl
from fcp.specs.struct import Struct
from fcp.specs.struct_field import StructField
from fcp.specs.enum import Enum, Enumeration
from fcp.specs.service import Service
from fcp.specs.type import ComposedType, ComposedTypeCategory


def _create_service_id_field() -> StructField:
    return StructField(
        name="service_id",
        field_id=0,
        type=ComposedType("ServiceId", ComposedTypeCategory.Enum),
    )


def _create_method_id_field(service: Service) -> StructField:
    return StructField(
        name="method_id",
        field_id=1,
        type=ComposedType(service.name + "MethodId", ComposedTypeCategory.Enum),
    )


def _create_payload(payload: Struct) -> StructField:
    return StructField(
        name="payload",
        field_id=2,
        type=ComposedType(payload.name, ComposedTypeCategory.Struct),
    )


def _rpc_input_struct(service: Service, payload: Struct) -> Struct:
    payload_type_name = payload.name + "Input"
    return Struct(
        name=payload_type_name,
        fields=[
            _create_service_id_field(),
            _create_method_id_field(service),
            _create_payload(payload),
        ],
    )


def _rpc_input_impl(payload: Struct) -> Impl:
    payload_type_name = payload.name + "Input"
    impl = Impl(
        name=payload_type_name,
        protocol="default",
        type=payload_type_name,
        fields={},
        signals=[],
        meta=None,
    )

    impl._is_method_input = True
    return impl


def _rpc_input_data(service: Service, payload: Struct) -> Struct:
    return _rpc_input_struct(service, payload), _rpc_input_impl(payload)


def _rpc_output_struct(service: Service, payload: Struct) -> Struct:
    payload_type_name = payload.name + "Output"
    return Struct(
        name=payload_type_name,
        fields=[
            _create_service_id_field(),
            _create_method_id_field(service),
            _create_payload(payload),
        ],
    )


def _rpc_output_impl(payload: Struct) -> Impl:
    payload_type_name = payload.name + "Output"
    return Impl(
        name=payload_type_name,
        protocol="default",
        type=payload_type_name,
        fields={},
        signals=[],
        meta=None,
    )


def _rpc_output_data(service: Service, payload: Struct) -> Struct:
    return _rpc_output_struct(service, payload), _rpc_output_impl(payload)


def _set_bitsize(enum: Enum, bitsize: int) -> Enum:
    m = max([e.value for e in enum.enumeration])

    size = 2**bitsize - 1
    if m > size:
        raise ValueError(f"{enum.name} must fit in {bitsize} bits")
    elif m < size:
        enum.enumeration.append(Enumeration("Size", size, None))

    return enum


def _create_service_id_enum(fcp: FcpV2) -> Enum:
    return _set_bitsize(
        Enum(
            name="ServiceId",
            enumeration=[
                Enumeration(service.name, service.id, None) for service in fcp.services
            ],
            meta=None,
        ),
        bitsize=8,
    )


def _create_method_id_enum(
    service_name: str, service_method_enum: Tuple[str, int]
) -> Enum:
    return _set_bitsize(
        Enum(
            name=service_name + "MethodId",
            enumeration=[
                Enumeration(method_name, id, None)
                for method_name, id in service_method_enum
            ],
            meta=None,
        ),
        bitsize=8,
    )


def _generate_enums(fcp: FcpV2, service_methods_enum: Tuple[str, int]) -> FcpV2:
    if len(fcp.services) != 0:
        fcp.enums.append(_create_service_id_enum(fcp))

        for service_name, service_method_enum in service_methods_enum.items():
            fcp.enums.append(_create_method_id_enum(service_name, service_method_enum))

    return fcp


def generate_rpc(fcp: FcpV2) -> FcpV2:
    """Generate rpc types."""
    method_data: Dict[str, Tuple[Struct, Impl]] = {}
    service_methods_enum: Dict[str, Tuple[str, int]] = {}

    for service in fcp.services:
        service_methods_enum[service.name] = []
        for method in service.methods:
            method_data[method.input] = _rpc_input_data(
                service, fcp.get_struct(method.input).unwrap()
            )
            method_data[method.output] = _rpc_output_data(
                service, fcp.get_struct(method.output).unwrap()
            )
            service_methods_enum[service.name].append((method.name, method.id))

    for rpc_input_struct, rpc_input_impl in method_data.values():
        fcp.structs.append(rpc_input_struct)
        fcp.impls.append(rpc_input_impl)

    return _generate_enums(fcp, service_methods_enum)
