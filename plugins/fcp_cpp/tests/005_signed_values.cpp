#include "fcp_can.h"
#include "fcp.h"

#include "utest.h"

UTEST_MAIN()

UTEST(BasicStruct, DecodeSignedAndUnsignedStruct) {
    auto foo = fcp::S1{1,-2,3,-4,5,-6,7,-8,9,-10};
    std::vector<std::uint8_t> encoded = foo.encode().GetData();

    std::vector<uint8_t> bytes{
        0x01,
        0xfe,
        0x03,0x00,
        0xfc,0xff,
        0x05,0x00,0x00,
        0xfa,0xff,0xff,
        0x07,0x00,0x00,0x00,
        0xf8,0xff,0xff,0xff,
        0x09,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
        0xf6,0xff,0xff,0xff,0xff,0xff,0xff,0xff};

    EXPECT_TRUE(encoded==bytes);
}

UTEST(BasicStruct, EncodeSignedAndUnsignedStruct) {
    std::vector<uint8_t> bytes{1,2,3,4,5,6,7,8,9,10};

    auto foo = fcp::S1::Encode(bytes.begin(), bytes.end());
    auto expected = fcp::S1{1,2,3,4,5,6,7,8,9,10};
    EXPECT_TRUE(foo==expected);
}
