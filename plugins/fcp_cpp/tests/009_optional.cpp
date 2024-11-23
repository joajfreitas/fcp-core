//#include "fcp_can.h"
#include "fcp.h"

#include "utest.h"

UTEST_MAIN()

UTEST(BasicStruct, EncodeOptionalWithValue) {
    auto s1 = fcp::S1{{1}};
    std::vector<std::uint8_t> encoded = s1.encode().GetData();

    std::vector<uint8_t> bytes{0x01, 0x1};

    EXPECT_TRUE(encoded==bytes);
}

UTEST(BasicStruct, EncodeOptionalWithNoValue) {
    auto s1 = fcp::S1{fcp::Optional<fcp::Unsigned<std::uint8_t, 8>>::None()};
    std::vector<std::uint8_t> encoded = s1.encode().GetData();

    std::vector<uint8_t> bytes{0x00};

    EXPECT_TRUE(encoded==bytes);
}

UTEST(BasicStruct, DecodeOptionalWithValue) {
    std::vector<uint8_t> bytes{0x01, 0x01};

    auto foo = fcp::S1::Decode(bytes.begin(), bytes.end());
    auto expected = fcp::S1{{1}};

    EXPECT_TRUE(foo==expected);
}

UTEST(BasicStruct, DecodeOptionalWithNoValue) {
    std::vector<uint8_t> bytes{0x00};

    auto foo = fcp::S1::Decode(bytes.begin(), bytes.end());
    auto expected = fcp::S1{fcp::Optional<fcp::Unsigned<std::uint8_t, 8>>::None()};

    EXPECT_TRUE(foo==expected);
}
