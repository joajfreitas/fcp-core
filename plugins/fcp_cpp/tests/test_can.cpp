#include "can.h"
#include "fcp.h"

#include <gmock/gmock.h>
#include <gtest/gtest.h>

using testing::Eq;
using testing::Optional;
using testing::Pair;

using json = nlohmann::json;

TEST(Decode, Basic)
{
    fcp::can::frame_t frame { { 'b', 'u', 's', '1' }, 10, 2, { 1, 2 } };

    auto schema = fcp::StaticSchema {};
    auto can = fcp::can::Can { schema };
    const auto decoded = can.Decode(frame);

    EXPECT_THAT(decoded,
        Optional(
            Pair(
                Eq("S1"),
                Eq(json { { "s1", 1 }, { "s2", 2 } }))));
}

TEST(Encode, Basic)
{
    auto schema = fcp::StaticSchema {};
    auto can = fcp::can::Can { schema };
    const auto frame = can.Encode("S1", { { "s1", 1 }, { "s2", 2 } });

    fcp::can::frame_t expected { { 'b', 'u', 's', '1' }, 10, 2, { 1, 2 } };

    EXPECT_THAT(frame, Optional(Eq(expected)));
}
