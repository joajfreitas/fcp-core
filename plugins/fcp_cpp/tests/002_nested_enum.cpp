#include "fcp_can.h"
#include "fcp.h"

#include "utest.h"

UTEST_MAIN()

UTEST(BasicStruct, Decode) {
    auto foo = fcp::Foo{1,2,fcp::E::S1};
    auto encoded = encode(foo);

    std::vector<uint8_t> bytes{1,2,1};
    EXPECT_TRUE(encoded == bytes);
}

UTEST(BasicStruct, Encode) {
    std::vector<uint8_t> bytes{1,2,1};

    auto foo = fcp::decode<fcp::Foo>(bytes);
    auto expected = fcp::Foo{1,2, fcp::E::S1};
    EXPECT_TRUE(foo == expected);
}
