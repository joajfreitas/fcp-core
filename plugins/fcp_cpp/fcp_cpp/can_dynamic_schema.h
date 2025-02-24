#pragma once

#include <optional>
#include <iostream>

#include "dynamic.h"
#include "can.h"

namespace fcp {
namespace can {

class CanDynamicSchema: public ICanSchema {
    public:
        CanDynamicSchema(const dynamic::DynamicSchema& dynamic_schema): dynamic_schema_{dynamic_schema} {}

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
        return std::nullopt;
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

        dynamic::DynamicSchema dynamic_schema_;
};
}
}
