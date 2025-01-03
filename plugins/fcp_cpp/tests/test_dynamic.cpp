#include "fcp.h"
#include "dynamic.h"
#include <nlohmann/json.hpp>

#include <cstring>

#include "utest.h"

UTEST_MAIN()

UTEST(BasicStruct, DecodeSimpleUnsigendStruct) {
    fcp::dynamic::DynamicSchema schema{};

    schema.LoadBinarySchemaFromFile("output.bin");

    auto decoded = schema.Decode("S1", {1,2});

    EXPECT_TRUE(decoded["s1"] == 1);
    EXPECT_TRUE(decoded["s2"] == 2);
}
