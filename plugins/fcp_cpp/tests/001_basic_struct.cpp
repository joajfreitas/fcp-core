#include "fcp_can.h"
#include "fcp.h"

#include "utest.h"

UTEST_MAIN()

UTEST(BasicStruct, DecodeSimpleUnsignedStruct) {
    auto foo = fcp::S1{1,2};
    auto encoded = foo.encode().GetData();

    std::vector<uint8_t> bytes{1,2};
    EXPECT_TRUE(encoded==bytes);
}

UTEST(BasicStruct, EncodeSimpleUnsignedStruct) {
    std::vector<uint8_t> bytes{1,2};

    auto foo = fcp::S1::Encode(bytes.begin(), bytes.end());
    auto expected = fcp::S1{1,2};
    EXPECT_TRUE(foo==expected);
}

UTEST(BasicStruct, DecodeSignedAndUnsignedStruct) {
    auto foo = fcp::S2{1,2,3,4,5,6,7,8,9,10};
    std::vector<std::uint8_t> encoded = foo.encode().GetData();

    std::vector<uint8_t> bytes{
        1,
        2,
        3,0,
        4,0,
        5,0,0,
        6,0,0,
        7,0,0,0,
        8,0,0,0,
        9,0,0,0,0,0,0,0,
        10,0,0,0,0,0,0,0};

    EXPECT_TRUE(encoded==bytes);
}

UTEST(BasicStruct, EncodeSignedAndUnsignedStruct) {
    std::vector<uint8_t> bytes{1,2,3,4,5,6,7,8,9,10};

    auto foo = fcp::S2::Encode(bytes.begin(), bytes.end());
    auto expected = fcp::S2{1,2,3,4,5,6,7,8,9,10};
    EXPECT_TRUE(foo==expected);
}

UTEST(BasicStruct, GetDeviceName) {
    EXPECT_TRUE(fcp::can::get_device_name(10) == "ecu1");
}
