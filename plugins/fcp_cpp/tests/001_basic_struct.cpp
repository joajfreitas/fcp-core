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

UTEST(BasicStruct, GetDeviceName) {
    EXPECT_TRUE(fcp::can::get_device_name(10) == "ecu1");
}
