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
