#include "can.h"
#include "fcp.h"

#include <gtest/gtest.h>
#include <gmock/gmock.h>

using testing::Eq;
using testing::Optional;

TEST(Decode, Basic) {
    fcp::can::frame_t frame{{'b','u','s','1'}, 10, 2, {1,2}};

    auto schema = fcp::StaticSchema{};
    auto can = fcp::can::Can{schema};
    const auto decoded = can.Decode(frame);

    ASSERT_TRUE(decoded.has_value()) << "Basic precondition failed. Decoding failed";

    const auto [msg_name, signals] = decoded.value();

    EXPECT_THAT(msg_name, Eq("S1"));
    EXPECT_THAT(signals["s1"], Eq(1));
    EXPECT_THAT(signals["s2"], Eq(2));
}

TEST(Encode, Basic) {
    //fcp::can::frame_t frame{{'b','u','s','1'}, 10, 2, {1,2}};

    auto schema = fcp::StaticSchema{};
    auto can = fcp::can::Can{schema};
    const auto frame = can.Encode("S1", {{"s1", 1}, {"s2", 2}});

    fcp::can::frame_t expected{{'b','u','s','1'}, 10, 2, {1,2}};

    EXPECT_THAT(frame, Optional(Eq(expected)));
}
