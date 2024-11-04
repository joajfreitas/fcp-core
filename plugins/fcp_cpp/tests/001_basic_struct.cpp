#include "fcp_can.h"
#include "fcp.h"

#include "utest.h"

UTEST_MAIN()

UTEST(BasicStruct, Decode) {
    auto foo = fcp::Foo{1,2};
    auto encoded = foo.encode();

    std::vector<uint8_t> bytes{1,2};
    EXPECT_TRUE(encoded==bytes);
}

UTEST(BasicStruct, Encode) {
    std::vector<uint8_t> bytes{1,2};

    auto foo = fcp::Foo::decode(bytes.begin());
    auto expected = fcp::Foo{1,2};
    EXPECT_TRUE(foo==expected);
}

UTEST(BasicStruct, GetDeviceName) {
    EXPECT_TRUE(fcp::can::Fcp::get_device_name(10) == "ecu1");
}
