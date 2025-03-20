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

#include "can.h"
#include "fcp.h"
#include "can_static_schema.h"
#include "can_dynamic_schema.h"

#include <memory>

#include <gmock/gmock.h>
#include <gtest/gtest.h>

using testing::Eq;
using testing::Optional;
using testing::Pair;
using testing::Values;

using json = nlohmann::json;

using CanTest = testing::TestWithParam<fcp::can::Can>;

fcp::can::CanDynamicSchema BuildCanDynamicSchema() {
    auto dynamic_schema = fcp::dynamic::DynamicSchema();
    dynamic_schema.LoadBinarySchemaFromFile("output.bin");
    return fcp::can::CanDynamicSchema(dynamic_schema);
}

INSTANTIATE_TEST_SUITE_P(, CanTest,
        Values(
            fcp::can::Can{std::make_shared<fcp::can::CanStaticSchema>(fcp::can::CanStaticSchema{})},
            fcp::can::Can{std::make_shared<fcp::can::CanDynamicSchema>(BuildCanDynamicSchema())}
        ));

TEST_P(CanTest, BasicDecode)
{
    auto can = GetParam();

    const auto decoded = can.Decode(fcp::can::frame_t{{'b','u','s','1'}, 10, 2, {1, 2}});

    EXPECT_THAT(decoded,
        Optional(
            Pair(
                Eq("S1"),
                Eq(json { { "s1", 1 }, { "s2", 2 } }))));
}

TEST_P(CanTest, BasicEncode)
{
    auto can = GetParam();

    const auto frame = can.Encode("S1", { { "s1", 1 }, { "s2", 2 } });

    EXPECT_THAT(frame, Optional(Eq(fcp::can::frame_t{{'b','u','s','1'}, 10, 2, {1,2}})));
}
