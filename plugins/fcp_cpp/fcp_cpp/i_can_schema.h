#pragma once

namespace fcp {
namespace can {

#include <nlohmann/json.hpp>

struct frame_t {
    std::array<char,4> bus;
    std::uint16_t sid;
    std::uint8_t dlc;
    std::array<std::uint8_t, 8> data;
};

class ICanSchema {
  public:
    virtual std::optional<std::pair<std::string, json>> Decode(const frame_t& frame) = 0;
    virtual std::optional<frame_t> Encode(std::string msg_name, json j) = 0;
};

}
}
