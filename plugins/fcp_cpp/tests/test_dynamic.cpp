#include <gmock/gmock.h>
#include <gtest/gtest.h>

#include "dynamic.h"
#include "fcp.h"
#include <nlohmann/json.hpp>

#include <cstring>

using json = nlohmann::json;

using testing::Eq;
using testing::Optional;

class DynamicSchemaTest : public testing::Test {
public:
    DynamicSchemaTest()
        : schema {}
    {
        schema.LoadBinarySchemaFromFile("output.bin");
    }

    fcp::dynamic::DynamicSchema GetSchema()
    {
        return schema;
    }

private:
    fcp::dynamic::DynamicSchema schema;
};

TEST_F(DynamicSchemaTest, DecodeSimpleUnsignedStruct)
{
    auto schema = GetSchema();

    auto decoded = schema.DecodeJson("S1", { 1, 2 });

    EXPECT_THAT(decoded, Optional(Eq(json { { "s1", 1 }, { "s2", 2 } })));
}


TEST_F(DynamicSchemaTest, DecodeIntegerStruct)
{
    auto schema = GetSchema();

    auto decoded = schema.DecodeJson("S5", { 1, 2, 3, 0, 4, 0, 5, 0, 0, 6, 0, 0, 7, 0, 0, 0, 8, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0 });

    EXPECT_THAT(decoded, Optional(Eq(json { { "s1", 1 }, { "s2", 2 }, { "s3", 3 }, { "s4", 4 }, { "s5", 5 }, { "s6", 6 }, { "s7", 7 }, { "s8", 8 }, { "s9", 9 }, { "s10", 10 } })));
}


TEST_F(DynamicSchemaTest, DecodeStaticArray)
{
    auto schema = GetSchema();

    auto decoded = schema.DecodeJson("S3", { 1, 2, 3, 4, 5, 6 });

    EXPECT_THAT(decoded, Optional(Eq(json { { "s1", { 1, 2, 3, 4 } }, { "s2", 5 }, { "s3", 6 } })));


}
