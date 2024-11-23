//#include "fcp_can.h"
#include "fcp.h"

#include "utest.h"

UTEST_MAIN()

UTEST(SimpleArray, Encode) {
    auto foo = fcp::Foo{{fcp::State::S0,fcp::State::S1,fcp::State::S2,fcp::State::S0}, 5,6};
    auto encoded = foo.encode().GetData();

    std::vector<uint8_t> bytes{0x24,5,6};
    EXPECT_TRUE(encoded == bytes);
}

UTEST(SimpleArray, Decode) {
    std::vector<uint8_t> bytes{0x24,5,6};

    auto foo = fcp::Foo::Decode(bytes.begin(), bytes.end());
    auto expected = fcp::Foo{{fcp::State::S0,fcp::State::S1,fcp::State::S2,fcp::State::S0}, 5, 6};

    EXPECT_TRUE(foo == expected);
}
