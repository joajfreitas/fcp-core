from beartype.typing import Dict, Any

from .specs.v2 import FcpV2
from .specs.impl import Impl
from .encoding import make_encoder, PackedEncoderContext, Value


def _set_bit(buffer, bit, bit_index):
    byte_address = bit_index >> 3
    intra_byte_bit_address = bit_index & 0b111

    buffer += bytearray([0] * (byte_address + 1 - len(buffer)))
    buffer[byte_address] = (
        buffer[byte_address] & ~(1 << intra_byte_bit_address)
        | bit << intra_byte_bit_address
    )


def _set_word(buffer, word, bitstart, bitlength):
    for i in range(bitlength):
        _set_bit(buffer, (word >> i) & 1, bitstart + i)


def _encode_value(value: Value, data: Dict[str, Any], buffer: bytearray):
    _set_word(buffer, data[value.name], value.bitstart, value.bitlength)


def encode(
    fcp: FcpV2, msg_name: str, data: Dict[str, Any], protocol="none"
) -> bytearray:
    encoder = make_encoder("packed", fcp, PackedEncoderContext())
    struct = fcp.get_struct(msg_name).unwrap()
    impl = fcp.get_matching_impl(struct, protocol)

    if impl.is_nothing():
        impl = Impl(
            name=struct.name, protocol="none", type=struct.name, fields={}, signals=[]
        )
    encoding = encoder.generate(impl)

    buffer = bytearray()
    for encodeable_piece in encoding:
        if isinstance(encodeable_piece, Value):
            _encode_value(encodeable_piece, data, buffer)
        encodeable_piece

    return buffer
