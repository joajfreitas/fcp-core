#include "fcp_can.h"
#include "fcp.h"

#include <gtest/gtest.h>

TEST(BasicStruct, Decode) {
    auto foo = fcp::Foo{1,2,fcp::E::S1};
    auto encoded = encode(foo);
    
    std::vector<uint8_t> bytes{1,2,1};
    EXPECT_EQ(encoded,bytes);
}

TEST(BasicStruct, Encode) {
    std::vector<uint8_t> bytes{1,2,1};

    auto foo = fcp::decode<fcp::Foo>(bytes);
    auto expected = fcp::Foo{1,2, fcp::E::S1};
    EXPECT_EQ(foo, expected);
}

int main(int argc, char **argv) {
    testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
