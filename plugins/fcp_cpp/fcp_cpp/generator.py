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


class Generator(CodeGenerator):
    """Cpp code generator."""

    def __init__(self) -> None:
        pass

    def _fcp_header(self) -> str:
        return """
#ifndef __FCP_H__
#define __FCP_H__

#include <vector>
#include <cstdint>
#include <iostream>
#include <map>
#include <any>

namespace fcp {

{% for enum in fcp.enums -%}
enum {{enum.name}} {
    {% for enumeration in enum.enumeration -%}
    {{enumeration.name}} = {{enumeration.value}},
    {% endfor %}
};

{% endfor -%}

{% for struct, impl in structs -%}
struct {{struct.name}} {
    {% for signal in struct.fields -%}
    {{signal.type | to_cpp_type}} {{signal.name}};
    {% endfor %}

    {% if impl is not none %}
    std::map<std::string, std::any> to_dict() {
        std::map<std::string, std::any> results{};

        {%- for piece in impl[1] %}
        results["{{piece.name}}"] = {{piece.name}};
        {%- endfor %}
        return results;
    }
    {% endif %}

};

{% endfor -%}

std::vector<std::uint8_t> encode(uint8_t input) {
    return {input};
}

std::vector<std::uint8_t> encode(uint16_t input) {
    return {static_cast<uint8_t>((input >> 8) & 0xFF), static_cast<uint8_t>(input & 0xFF)};
}

std::vector<std::uint8_t> encode(uint32_t input) {
    return {
        static_cast<uint8_t>((input >> 24) & 0xFF),
        static_cast<uint8_t>((input >> 16) & 0xFF),
        static_cast<uint8_t>((input >>  8) & 0xFF),
        static_cast<uint8_t>((input >>  0) & 0xFF)
    };
}

{% for name, encoding in impls.items() %}
std::vector<std::uint8_t> encode(const {{name}}& input) {
    std::vector<std::uint8_t> result{};
    std::vector<std::uint8_t> aux{};
    {%- for encode_piece in encoding[1] %}
    aux = encode(input.{{encode_piece.name}});
    result.insert(result.begin(), aux.rbegin(), aux.rend());
    {%- endfor %}
    return result;
}
{% endfor %}

uint8_t get_bit(const std::vector<uint8_t>& input, uint8_t bit) {
    auto byte_address = bit / 8;
    auto intra_byte_bit_address = bit % 8;

    return (input[byte_address] >> intra_byte_bit_address) & 0b1;
}

template<typename T>
T _decode(const std::vector<uint8_t>&, uint8_t bitstart, uint8_t bitlength);

template<>
uint8_t _decode(const std::vector<uint8_t>& input, uint8_t bitstart, uint8_t bitlength) {
    uint8_t result = 0;

    for (int i=0; i<bitlength; i++) {
        result |= (get_bit(input, bitstart + i)) << i;
    }
    return result;
}

template<>
uint32_t _decode(const std::vector<uint8_t>& input, uint8_t bitstart, uint8_t bitlength) {
    uint32_t result = 0;

    for (int i=0; i<bitlength; i++) {
        result |= (get_bit(input, bitstart + i)) << i;
    }
    return result;
}

template<typename T>
T decode(const std::vector<uint8_t>&);

{% for name, encoding in impls.items() %}
template<>
{{name}} decode(const std::vector<uint8_t>& input) {
    {{name}} result{};

    {% for encode_piece in encoding[1] %}
    result.{{encode_piece.name}} = _decode<{{encode_piece.type | to_cpp_type()}}>(input, {{encode_piece.bitstart}}, {{encode_piece.bitlength}});
    {% endfor %}

    return result;
}
{% endfor %}

} // namespace fcp


#endif // __FCP_CAN_H__
"""

    def _can_header(self) -> str:
        return """#ifndef __FCP_CAN_H__
#define __FCP_CAN_H__

#include <map>
#include <any>

namespace fcp {
namespace can {

struct can_frame {
    uint16_t sid;
    uint8_t dlc;
    uint8_t data[8];
};

class Fcp {
public:
    struct DecodedMsg {
        std::string msg_name;
        std::map<std::string, std::any> signals;

        template<typename T>
        T get(std::string name) {
            return std::any_cast<T>(signals.at(name));
        }
    };

    DecodedMsg decode_msg(const can_frame& frame) {

        switch (frame.sid) {
        {% for impl in impls.values() %}
        case {{impl[0].fields.get('id')}}:
        return {"todo", decode<{{impl[0].type}}>(std::vector<std::uint8_t>{frame.data, frame.data + sizeof(frame.data)/sizeof(frame.data[0])}).to_dict()};
            break;
        {% endfor %}
        }

    }

    can_frame encode_msg(std::string dev_id, std::string msg_id, std::map<std::string, double> signals_list);
};

} // namesapce can
} // namespace fcp

#endif // __FCP_CAN_H__
    """

    # TODO: generate to string
    # TODO: operator_bool, operator==, operator!=
    # TODO: generate can frame encoding

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
        impls = {}

        for impl in fcp.get_matching_impls("can"):
            encoding = encoder.generate(impl)
            for encode_piece in encoding:
                encode_piece.name = encode_piece.name.replace("::", ".")

            impls[impl.type] = (impl, encoding)

        structs = [(struct, impls.get(struct.name)) for struct in fcp.structs]

        return [
            {
                "type": "file",
                "path": Path(ctx.get("output")) / "fcp.h",
                "contents": env.get_template("fcp_header").render(
                    {"fcp": fcp, "impls": impls, "structs": structs}
                ),
            },
            {
                "type": "file",
                "path": Path(ctx.get("output")) / "fcp_can.h",
                "contents": env.get_template("can_header").render(
                    {"fcp": fcp, "impls": impls, "structs": structs}
                ),
            },
        ]

    def register_checks(self, verifier: Verifier) -> NoReturn:  # type: ignore
        """Register cpp specific checks."""
        pass
