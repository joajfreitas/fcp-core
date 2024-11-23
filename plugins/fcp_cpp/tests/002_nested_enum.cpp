//#include "fcp_can.h"
#include "fcp.h"

#include "utest.h"

UTEST_MAIN()

UTEST(BasicStruct, Encode) {
    auto foo = fcp::Foo{1,2,fcp::E::S1};
    auto encoded = foo.encode().GetData();

    std::vector<uint8_t> bytes{1,2,1};
    EXPECT_TRUE(encoded == bytes);
}

UTEST(BasicStruct, Decode) {
    std::vector<uint8_t> bytes{1,2,1};

    auto foo = fcp::Foo::Decode(bytes.begin(), bytes.end());
    auto expected = fcp::Foo{1,2, fcp::E::S1};
    EXPECT_TRUE(foo == expected);
}
