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

#include <map>
#include <any>
#include <cstdint>
#include <string>
#include <optional>
#include <cstring>
#include <utility>

#include "fcp.h"
#include "i_can_schema.h"
#include "json.h"

namespace fcp {
namespace can {

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
