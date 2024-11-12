#include "fcp_can.h"
#include "fcp.h"

#include "utest.h"

UTEST_MAIN()

UTEST(SimpleArray, Decode) {
    auto foo = fcp::Foo{{1,2,3,4}, 5,6};
    auto encoded = foo.encode().GetData();

    std::vector<uint8_t> bytes{1,2,3,4,5,6};
    EXPECT_TRUE(encoded == bytes);
}

UTEST(SimpleArray, Encode) {
    std::vector<uint8_t> bytes{1,2,3,4,5,6};

    auto foo = fcp::Foo::Encode(bytes.begin(), bytes.end());
    auto expected = fcp::Foo{{1,2,3,4}, 5, 6};
    EXPECT_TRUE(foo == expected);
}
