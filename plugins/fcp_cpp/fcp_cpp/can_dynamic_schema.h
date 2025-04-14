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

#include <optional>
#include <iostream>

#include "dynamic.h"
#include "can.h"

namespace fcp {
namespace can {

class CanDynamicSchema final: public ICanSchema {
    public:
        CanDynamicSchema(const dynamic::DynamicSchema& dynamic_schema): dynamic_schema_{dynamic_schema} {}
        ~CanDynamicSchema() = default;

    std::optional<std::pair<std::string, json>> Decode(const frame_t& frame) override {
        auto msg_name = GetMsgName(frame.sid, frame.bus);
        if (!msg_name.has_value()) {
            return std::nullopt;
        }

        auto decoded = dynamic_schema_.DecodeJson(msg_name.value(), std::vector<std::uint8_t>{frame.data.begin(), frame.data.end()});

        if (!decoded.has_value()) {
            return std::nullopt;
        }

        return std::make_pair(msg_name.value(), decoded.value());
    }

    std::optional<frame_t> Encode(std::string msg_name, json j) override {
        auto encoded = dynamic_schema_.EncodeJson(msg_name, j);

        if (!encoded.has_value()) {
            return std::nullopt;
        }

        std::array<char, 4> bus_name = {0};
        std::copy(msg_name.begin(), msg_name.end(), bus_name.begin());

        auto id = GetId(msg_name);
        if (!id.has_value()) {
            return std::nullopt;
        }

        auto bus = GetBus(msg_name);
        if (!bus.has_value()) {
            return std::nullopt;
        }

        std::uint8_t dlc = encoded.value().size();
        std::array<std::uint8_t, 8> data = {0};
        std::copy(encoded.value().begin(), encoded.value().end(), data.begin());
        return frame_t{bus.value(), id.value(), dlc, data};
    }

    private:
        std::optional<std::string> GetMsgName(std::uint16_t sid, const std::array<char,4> bus_name) {
            std::string bus_name_str(bus_name.begin(), bus_name.end());

            auto impls = dynamic_schema_.GetImpls();
            for (const auto& impl: impls) {
                if (impl.protocol != "can") {
                    continue;
                }

                bool sid_match = impl.fields.find("id") != impl.fields.end() && sid == std::stoi(impl.fields.at("id"));

                bool bus_match = impl.fields.find("bus") != impl.fields.end() && bus_name_str == impl.fields.at("bus");

                if (sid_match && bus_match) {
                    return impl.name;
                }
            }

            return std::nullopt;
        }

        std::optional<std::uint16_t> GetId(std::string msg_name) {
            auto impls = dynamic_schema_.GetImpls();
            for (const auto& impl: impls) {
                if (impl.protocol != "can") {
                    continue;
                }

                if (impl.name == msg_name) {
                    return std::stoi(impl.fields.at("id"));
                }
            }

            return std::nullopt;
        }

        std::optional<std::array<char, 4>> GetBus(std::string msg_name) {
            auto impls = dynamic_schema_.GetImpls();
            for (const auto& impl: impls) {
                if (impl.protocol != "can") {
                    continue;
                }

                if (impl.name == msg_name) {
                    std::array<char, 4> bus_name = {0};
                    std::copy(impl.fields.at("bus").begin(), impl.fields.at("bus").end(), bus_name.begin());
                    return bus_name;
                }
            }

            return std::nullopt;
        }

        dynamic::DynamicSchema dynamic_schema_;
};

}
}
