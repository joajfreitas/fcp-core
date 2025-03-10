#pragma once

#include <map>
#include <any>
#include <cstdint>
#include <string>
#include <optional>
#include <cstring>
#include <utility>

#include <nlohmann/json.hpp>

#include "fcp.h"
#include "i_can_schema.h"

namespace fcp {
namespace can {

using json = nlohmann::json;

inline bool operator==(const frame_t& lhs, const frame_t& rhs) {
    return lhs.bus == rhs.bus &&
            lhs.sid == rhs.sid &&
            lhs.dlc == rhs.dlc &&
            lhs.data == rhs.data;
}

struct Can {
    Can(std::shared_ptr<ICanSchema> schema): schema_{std::move(schema)} {}

    std::optional<std::pair<std::string,json>> Decode(const frame_t& frame) {
        return schema_->Decode(frame);
    }

    std::optional<frame_t> Encode(std::string msg_name, json j) {
        return schema_->Encode(msg_name, j);
    }

  private:
    std::shared_ptr<ICanSchema> schema_;
};

} // namesapce can
} // namespace fcp
