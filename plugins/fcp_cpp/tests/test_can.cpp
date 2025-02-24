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

using CanTest = testing::TestWithParam<std::shared_ptr<fcp::can::ICanSchema>>;

std::shared_ptr<fcp::can::CanDynamicSchema> BuildCanDynamicSchema() {
    auto dynamic_schema = fcp::dynamic::DynamicSchema();
    dynamic_schema.LoadBinarySchemaFromFile("output.bin");
    return std::make_shared<fcp::can::CanDynamicSchema>(dynamic_schema);
}

INSTANTIATE_TEST_SUITE_P(, CanTest,
        Values(
            std::make_shared<fcp::can::CanStaticSchema>(),
            BuildCanDynamicSchema()
        ));

TEST_P(CanTest, BasicDecode)
{
    fcp::can::frame_t frame { { 'b', 'u', 's', '1' }, 10, 2, { 1, 2 } };

    auto schema = GetParam();
    auto can = fcp::can::Can ( *schema );
    const auto decoded = can.Decode(frame);

    EXPECT_THAT(decoded,
        Optional(
            Pair(
                Eq("S1"),
                Eq(json { { "s1", 1 }, { "s2", 2 } }))));
}

TEST_F(CanTest, BasicEncode)
{
    auto schema = fcp::can::CanStaticSchema();
    auto can = fcp::can::Can ( schema );
    const auto frame = can.Encode("S1", { { "s1", 1 }, { "s2", 2 } });

    fcp::can::frame_t expected { { 'b', 'u', 's', '1' }, 10, 2, { 1, 2 } };

    EXPECT_THAT(frame, Optional(Eq(expected)));
}
