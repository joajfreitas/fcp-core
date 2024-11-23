#include <iostream>

//#include "fcp_can.h"
#include "fcp.h"

#include "utest.h"

UTEST_MAIN()

UTEST(BasicStruct, EncodeString) {
    auto s1 = fcp::S1{{{0,1,2}}};
    std::vector<std::uint8_t> encoded = s1.encode().GetData();

    std::vector<uint8_t> bytes{
        0x03, 0x00, 0x00, 0x00,
        0x00, 0x01, 0x02};


    EXPECT_TRUE(encoded==bytes);
}

UTEST(BasicStruct, DecodeString) {
    std::vector<uint8_t> bytes{
        0x03, 0x00, 0x00, 0x00,
        0x00, 0x01, 0x02};

    auto foo = fcp::S1::Decode(bytes.begin(), bytes.end());
    auto expected = fcp::S1{{{0,1,2}}};

    EXPECT_TRUE(foo==expected);
}
