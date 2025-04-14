// Copyright (c) 2024 the fcp AUTHORS.
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.

// Generated using fcp {{version}} on {{date}} by {{user}}@{{hostname}}

// DO NOT EDIT

#pragma once

#include "fcp.h"
#include "can.h"

namespace fcp {
namespace can {

class CanStaticSchema: public ICanSchema {
  public:
    CanStaticSchema(): static_schema_{} {}
    ~CanStaticSchema() = default;

    std::optional<std::pair<std::string, json>> Decode(const frame_t& frame) override {
        auto msg_name = GetMsgName(frame.sid, frame.bus);

        if (!msg_name.has_value()) {
            return std::nullopt;
        }
        auto decoded = static_schema_.DecodeJson(msg_name.value(), std::vector<std::uint8_t>{frame.data.begin(), frame.data.end()});

        if (!decoded.has_value()) {
            return std::nullopt;
        }

        return std::make_pair(msg_name.value(), decoded.value());
    }

    std::optional<frame_t> Encode(std::string msg_name, json j) override {
        auto encoded = static_schema_.EncodeJson(msg_name, j);

        if (!encoded.has_value()) {
            return std::nullopt;
        }

        auto bus_name = GetBus(msg_name);
        if (!bus_name.has_value()) {
            return std::nullopt;
        }

        auto sid = GetSid(msg_name);
        if (!sid.has_value()) {
            return std::nullopt;
        }

        std::array<std::uint8_t, 8> data{};
        std::copy_n(encoded.value().begin(), encoded.value().size(), data.begin());

        std::array<char, 4> bus_name_arr{};
        std::copy_n(bus_name.value().begin(), 4, bus_name_arr.begin());
        return frame_t{
            bus_name_arr,
            sid.value(),
            static_cast<std::uint8_t>(encoded.value().size()),
            data
        };
    }

  private:
    std::optional<std::string> GetMsgName(std::uint16_t sid, const std::array<char,4> bus_name) {
        std::string bus_name_str(bus_name.begin(), bus_name.end());

        {% for impl in fcp.get_matching_impls("can") %}
        if (sid == {{impl.fields.get('id')}} && bus_name_str == "{{impl.fields.get('bus', 'unkn')}}") {
            return "{{impl.name}}";
        }
        {% endfor %}

        return std::nullopt;
    }

    std::optional<std::uint16_t> GetSid(std::string msg_name) {
        {% for impl in fcp.get_matching_impls("can") %}
        if (msg_name == "{{impl.name}}") {
            return {{impl.fields.get('id')}};
        }
        {% endfor %}

        return std::nullopt;
    }

    std::optional<std::string> GetBus(std::string msg_name) {
        {% for impl in fcp.get_matching_impls("can") %}
        if (msg_name == "{{impl.name}}") {
            return "{{impl.fields.get('bus')}}";
        }
        {% endfor %}

        return "unkn";
    }

    StaticSchema static_schema_;
};

}
}
