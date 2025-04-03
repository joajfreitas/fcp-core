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

"""Serialization/Deserialization library using fcp schemas."""

from beartype.typing import Dict, Any, Union, List
import struct

from .specs.v2 import FcpV2
from .specs.type import (
    Type,
    ArrayType,
    StructType,
    DynamicArrayType,
    OptionalType,
    StringType,
    UnsignedType,
    SignedType,
    FloatType,
    DoubleType,
)


class _Buffer:
    def __init__(self) -> None:
        self.buffer: List[int] = []
        self.bitaddr: int = 0

    def set_bit(self, bit: int, bitaddr: int) -> None:
        byte_addr = bitaddr >> 3
        intra_byte_bit_addr = bitaddr & 0x7

        if len(self.buffer) <= byte_addr:
            self.buffer.append(0)

        self.buffer[byte_addr] |= bit << intra_byte_bit_addr

    def get_bit(self, bitaddr: int) -> int:
        byte_addr = bitaddr >> 3
        intra_byte_bit_addr = bitaddr & 0x7

        if len(self.buffer) <= byte_addr:
            raise ValueError("buffer overrrun")

        return int((self.buffer[byte_addr] >> intra_byte_bit_addr) & 1)

    def push_word(self, word: int, bits: int) -> None:
        for i in range(bits):
            self.set_bit(word >> i & 1, self.bitaddr + i)

        self.bitaddr += bits

    def push_bytes(self, bytes: List[int]) -> None:
        self.buffer += bytes

    def read_word(self, bits: int) -> int:
        word = 0
        for i in range(bits):
            word |= (self.get_bit(self.bitaddr + i)) << i

        self.bitaddr += bits
        return word

    def read_bytes(self, bytes: int) -> List[int]:
        byteaddr = self.bitaddr >> 3
        self.bitaddr += 8 * bytes
        return self.buffer[byteaddr : byteaddr + bytes]

    def get_buffer(self) -> bytearray:
        return bytearray(self.buffer)


def _encode_builtin_unsigned(buffer: _Buffer, type: UnsignedType, data: Any) -> None:
    length = type.get_length()
    buffer.push_word(data, length)


def _encode_builtin_signed(buffer: _Buffer, type: SignedType, data: Any) -> None:
    length = type.get_length()
    buffer.push_word(data, length)


def _encode_builtin_float(buffer: _Buffer, type: FloatType, data: Any) -> None:
    v = struct.pack("f", data)
    buffer.push_bytes(list(v))


def _encode_builtin_double(buffer: _Buffer, type: DoubleType, data: Any) -> None:
    v = struct.pack("d", data)
    buffer.push_bytes(list(v))


def _encode_str(buffer: _Buffer, fcp: FcpV2, type: StringType, data: Any) -> None:
    _encode_builtin_unsigned(buffer, UnsignedType("u32"), len(data))
    for x in data:
        _encode(buffer, fcp, UnsignedType("u8"), ord(x))


def _encode_struct(
    buffer: _Buffer, fcp: FcpV2, name: str, data: Dict[str, Any]
) -> None:
    struct = fcp.get_struct(name).unwrap()

    for field in struct.fields:
        _encode(buffer, fcp, field.type, data[field.name])


def _encode_array(buffer: _Buffer, fcp: FcpV2, type: ArrayType, data: Any) -> None:
    for i in range(type.size):
        _encode(buffer, fcp, type.underlying_type, data[i])


def _encode_dynamic_array(
    buffer: _Buffer, fcp: FcpV2, type: DynamicArrayType, data: Any
) -> None:
    _encode_builtin_unsigned(buffer, UnsignedType("u32"), len(data))

    for x in data:
        _encode(buffer, fcp, type.underlying_type, x)


def _encode_optional(
    buffer: _Buffer, fcp: FcpV2, type: OptionalType, data: Any
) -> None:

    is_some = data is not None
    _encode_builtin_unsigned(buffer, UnsignedType("u8"), 1 if is_some else 0)
    if is_some:
        _encode(buffer, fcp, type.underlying_type, data)


def _encode(
    buffer: _Buffer, fcp: FcpV2, type: Type, data: Union[Any, Dict[str, Any]]
) -> None:

    if isinstance(type, UnsignedType):
        _encode_builtin_unsigned(buffer, type, data)
    elif isinstance(type, SignedType):
        _encode_builtin_signed(buffer, type, data)
    elif isinstance(type, FloatType):
        _encode_builtin_float(buffer, type, data)
    elif isinstance(type, DoubleType):
        _encode_builtin_double(buffer, type, data)
    elif isinstance(type, StringType):
        _encode_str(buffer, fcp, type, data)
    elif isinstance(type, StructType):
        _encode_struct(buffer, fcp, type.name, data)
    elif isinstance(type, ArrayType):
        _encode_array(buffer, fcp, type, data)
    elif isinstance(type, DynamicArrayType):
        _encode_dynamic_array(buffer, fcp, type, data)
    elif isinstance(type, OptionalType):
        _encode_optional(buffer, fcp, type, data)
    else:
        raise ValueError("Unmatched type " + str(type))


def encode(fcp: FcpV2, name: str, data: Dict[str, Any]) -> bytearray:
    """Encode data using fcp schema."""
    buffer = _Buffer()
    _encode_struct(buffer, fcp, name, data)
    return buffer.get_buffer()


def _decode_builtin_unsigned(buffer: _Buffer, type: UnsignedType) -> int:
    length = type.get_length()
    return buffer.read_word(length)


def _decode_builtin_signed(buffer: _Buffer, type: SignedType) -> int:
    length = type.get_length()
    word = buffer.read_word(length)

    max = 2**length
    if word > max / 2:
        return int(-(max - word))
    else:
        return int(word)


def _decode_builtin_float(buffer: _Buffer, type: FloatType) -> float:
    return float(struct.unpack("f", bytearray(buffer.read_bytes(4)))[0])


def _decode_builtin_double(buffer: _Buffer, type: DoubleType) -> float:
    return float(struct.unpack("d", bytearray(buffer.read_bytes(8)))[0])


def _decode_str(buffer: _Buffer, type: StringType) -> str:
    len = _decode_builtin_unsigned(buffer, UnsignedType("u32"))
    return bytearray(buffer.read_bytes(len)).decode("ascii")


def _decode_array(buffer: _Buffer, fcp: FcpV2, type: ArrayType) -> List[Any]:
    data = []
    for i in range(type.size):
        data.append(_decode(buffer, fcp, type.underlying_type))

    return data


def _decode_dynamic_array(
    buffer: _Buffer, fcp: FcpV2, type: DynamicArrayType
) -> List[Any]:
    len = _decode_builtin_unsigned(buffer, UnsignedType("u32"))
    data = []
    for i in range(len):
        data.append(_decode(buffer, fcp, type.underlying_type))

    return data


def _decode_optional(buffer: _Buffer, fcp: FcpV2, type: OptionalType) -> List[Any]:
    is_some = _decode_builtin_unsigned(buffer, UnsignedType("u8")) != 0
    if is_some:
        return _decode(buffer, fcp, type.underlying_type)
    else:
        return None


def _decode_struct(buffer: _Buffer, fcp: FcpV2, name: str) -> Dict[str, Any]:
    struct = fcp.get_struct(name).unwrap()

    data = {}
    for field in struct.fields:
        data[field.name] = _decode(buffer, fcp, field.type)

    return data


def _decode(buffer: _Buffer, fcp: FcpV2, type: Type) -> Dict[str, Any]:
    if isinstance(type, UnsignedType):
        return _decode_builtin_unsigned(buffer, type)
    elif isinstance(type, SignedType):
        return _decode_builtin_signed(buffer, type)
    elif isinstance(type, FloatType):
        return _decode_builtin_float(buffer, type)
    elif isinstance(type, DoubleType):
        return _decode_builtin_double(buffer, type)
    elif isinstance(type, StringType):
        return _decode_str(buffer, type)
    elif isinstance(type, StructType):
        return _decode_struct(buffer, fcp, type.name)
    elif isinstance(type, ArrayType):
        return _decode_array(buffer, fcp, type)
    elif isinstance(type, DynamicArrayType):
        return _decode_dynamic_array(buffer, fcp, type)
    elif isinstance(type, OptionalType):
        return _decode_optional(buffer, fcp, type)
    else:
        raise ValueError("Unmatched type")


def decode(fcp: FcpV2, name: str, data: bytearray) -> Dict[str, Any]:
    """Decode bytearray using fcp schema."""
    buffer = _Buffer()
    buffer.push_bytes(list(data))
    buffer.bitaddr = 0

    return _decode_struct(buffer, fcp, name)
