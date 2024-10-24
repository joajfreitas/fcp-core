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
        self.dlc = math.ceil((encoding[-1].bitstart + encoding[-1].bitlength) / 8)


class Generator(CodeGenerator):
    """Cpp code generator."""

    def __init__(self) -> None:
        pass

    def _fcp_header(self) -> str:
        return """#ifndef __FCP_H__
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
    {% endfor -%}

    {% if impl is not none %}
    std::map<std::string, std::tuple<std::any, std::string>> to_dict() {
        std::map<std::string, std::tuple<std::any, std::string>> results{};

        {%- for piece in impl.encoding %}
        results["{{piece.name}}"] = std::make_tuple({{piece.name}}, "{{piece.type | to_cpp_type }}");
        {%- endfor -%}
        return results;
    }
    {% endif -%}

    {% if impl is not none %}
    static {{struct.name}} from_dict(std::map<std::string, std::tuple<std::any, std::string>> dict) {
        {{struct.name}} result{};
        {%- for piece in impl.encoding %}
        result.{{piece.name}} = std::any_cast<{{piece.type | to_cpp_type}}>(std::get<0>(dict["piece.name"]));
        {%- endfor -%}
        return result;
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

{% for name, encoding in can_encodings.items() %}
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
    auto byte_address = bit >> 3;
    auto intra_byte_bit_address = bit & 0b111;

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

{% for name, can_encoding in can_encodings.items() %}
template<>
{{name}} decode(const std::vector<uint8_t>& input) {
    {{name}} result{};
    {% for encode_piece in can_encoding.encoding %}
    result.{{encode_piece.name}} = _decode<{{encode_piece.type | to_cpp_type()}}>(input, {{encode_piece.bitstart}}, {{encode_piece.bitlength}});
    {%- endfor %}

    return result;
}
{% endfor -%}

} // namespace fcp


#endif // __FCP_CAN_H__"""

    def _can_header(self) -> str:
        return """#ifndef __FCP_CAN_H__
#define __FCP_CAN_H__

#include <map>
#include <any>
#include <cstdint>
#include <string>
#include <optional>
#include <cstring>

#include "fcp.h"

namespace fcp {
namespace can {

struct can_frame {
    std::uint16_t sid;
    std::uint8_t dlc;
    std::uint8_t data[8];
};

class Fcp {
public:
    struct DecodedMsg {
        std::string msg_name;
        std::map<std::string, std::tuple<std::any, std::string>> signals;

        template<typename T>
        T _get(std::string name) {
            return std::any_cast<T>(std::get<0>(signals.at(name)));
        }


        template<typename T>
        T get(std::string name) {
            auto type = std::get<1>(signals.at(name));

            if (type == "uint8_t") {
                return static_cast<T>(_get<uint8_t>(name));
            }
            else if (type == "uint16_t") {
                return static_cast<T>(_get<uint16_t>(name));
            }
            else if (type == "uint32_t") {
                return static_cast<T>(_get<uint32_t>(name));
            }
            else if (type == "uint64_t") {
                return static_cast<T>(_get<uint64_t>(name));
            }
            else if (type == "int8_t") {
                return static_cast<T>(_get<int8_t>(name));
            }
            else if (type == "int16_t") {
                return static_cast<T>(_get<int16_t>(name));
            }
            else if (type == "int32_t") {
                return static_cast<T>(_get<int32_t>(name));
            }
            else if (type == "int64_t") {
                return static_cast<T>(_get<int64_t>(name));
            }
            else if (type == "float") {
                return static_cast<T>(_get<float>(name));
            }
            else if (type == "double") {
                return static_cast<T>(_get<double>(name));
            }
            else {
                return T{};
            }
        }
    };

    std::optional<DecodedMsg> decode_msg(const can_frame& frame) {

        switch (frame.sid) {
        {% for can_encoding in can_encodings.values() %}
        case {{can_encoding.impl.fields.get('id')}}:
        return DecodedMsg{"{{can_encoding.impl.name}}", decode<{{can_encoding.impl.type}}>(std::vector<std::uint8_t>{frame.data, frame.data + sizeof(frame.data)/sizeof(frame.data[0])}).to_dict()};
            break;
        {% endfor %}
        }

        return std::nullopt;

    }

    std::optional<can_frame> encode_msg(std::string msg_name, std::map<std::string, std::tuple<std::any, std::string>> signals) {

        can_frame frame{};
        {% for can_encoding in can_encodings.values() %}
        if (msg_name == "{{can_encoding.impl.name}}") {
            auto encoded = encode({{can_encoding.impl.name}}::from_dict(signals));
            frame.sid = {{can_encoding.id}};
            frame.dlc = {{can_encoding.dlc}};

            std::memcpy(frame.data, encoded.data(), {{can_encoding.dlc}});
            return frame;
        }
        {% endfor %}

        return std::nullopt;
    }
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
