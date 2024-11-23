//#include "fcp_can.h"
#include "fcp.h"

#include "utest.h"

UTEST_MAIN()

UTEST(BasicStruct, EncodeSignedAndUnsignedStruct) {
    auto foo = fcp::S1{1.0, 1.0};
    std::vector<std::uint8_t> encoded = foo.encode().GetData();

    std::vector<uint8_t> bytes{
        0x00, 0x00, 0x80, 0x3f,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xF0, 0x3F};


    EXPECT_TRUE(encoded==bytes);
}

UTEST(BasicStruct, DecodeSignedAndUnsignedStruct) {
    std::vector<uint8_t> bytes{
        0x00, 0x00, 0x80, 0x3f,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xF0, 0x3F};

    auto foo = fcp::S1::Decode(bytes.begin(), bytes.end());
    auto expected = fcp::S1{1.0, 1.0};

    EXPECT_TRUE(foo==expected);
}
