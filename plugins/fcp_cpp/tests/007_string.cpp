#include <iostream>

//#include "fcp_can.h"
#include "fcp.h"

#include "utest.h"

UTEST_MAIN()

UTEST(BasicStruct, EncodeString) {
    auto s1 = fcp::S1{"hello"};
    std::vector<std::uint8_t> encoded = s1.encode().GetData();

    std::vector<uint8_t> bytes{
        0x05, 0x00, 0x00, 0x00,
        0x68, 0x65, 0x6c, 0x6c, 0x6f};


    EXPECT_TRUE(encoded==bytes);
}

UTEST(BasicStruct, DecodeString) {
    std::vector<uint8_t> bytes{
        0x05, 0x00, 0x00, 0x00,
        0x68, 0x65, 0x6c, 0x6c, 0x6f};

    auto foo = fcp::S1::Decode(bytes.begin(), bytes.end());
    auto expected = fcp::S1{"hello"};

    EXPECT_TRUE(foo==expected);
}
