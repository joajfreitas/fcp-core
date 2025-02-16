#include <gtest/gtest.h>
#include <gmock/gmock.h>

#include "fcp.h"
#include "dynamic.h"
#include <nlohmann/json.hpp>

#include <cstring>

TEST(BasicStruct, DecodeSimpleUnsigendStruct) {
    fcp::dynamic::DynamicSchema schema{};

    schema.LoadBinarySchemaFromFile("output.bin");

    auto decoded = schema.DecodeJson("S1", {1,2}).value();

    EXPECT_THAT(decoded["s1"], 1);
    EXPECT_THAT(decoded["s2"], 2);
}
