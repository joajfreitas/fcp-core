#pragma once

#include "fcp.h"
#include "can.h"

namespace fcp {
namespace can {

class CanStaticSchema: public ICanSchema {
  public:
    CanStaticSchema(): static_schema_{} {}

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

        

        return std::nullopt;
    }

    std::optional<std::uint16_t> GetSid(std::string msg_name) {
        

        return std::nullopt;
    }

    std::optional<std::string> GetBus(std::string msg_name) {
        

        return "unkn";
    }

    StaticSchema static_schema_;
};

}
}