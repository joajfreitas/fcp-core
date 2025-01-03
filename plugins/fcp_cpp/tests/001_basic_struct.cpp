//#include "fcp_can.h"
#include "fcp.h"

#include "utest.h"

UTEST_MAIN()

UTEST(BasicStruct, EncodeSimpleUnsignedStruct) {
    auto foo = fcp::S1{1,2};
    auto encoded = foo.encode().GetData();

    std::vector<uint8_t> bytes{1,2};
    EXPECT_TRUE(encoded==bytes);
}

UTEST(BasicStruct, DecodeSimpleUnsignedStruct) {
    std::vector<uint8_t> bytes{1,2};

    auto foo = fcp::S1::Decode(bytes.begin(), bytes.end());
    auto expected = fcp::S1{1,2};
    EXPECT_TRUE(foo==expected);
}

UTEST(NestedEnum, Encode) {
    auto foo = fcp::S2{1,2,fcp::E::S1};
    auto encoded = foo.encode().GetData();

    std::vector<uint8_t> bytes{1,2,1};
    EXPECT_TRUE(encoded == bytes);
}

UTEST(NestedEnum, Decode) {
    std::vector<uint8_t> bytes{1,2,1};

    auto foo = fcp::S2::Decode(bytes.begin(), bytes.end());
    auto expected = fcp::S2{1,2, fcp::E::S1};
    EXPECT_TRUE(foo == expected);
}

UTEST(SimpleArray, Encode) {
    auto foo = fcp::S3{{1,2,3,4}, 5,6};
    auto encoded = foo.encode().GetData();

    std::vector<uint8_t> bytes{1,2,3,4,5,6};
    EXPECT_TRUE(encoded == bytes);
}

UTEST(SimpleArray, Decode) {
    std::vector<uint8_t> bytes{1,2,3,4,5,6};

    auto foo = fcp::S3::Decode(bytes.begin(), bytes.end());
    auto expected = fcp::S3{{1,2,3,4}, 5, 6};
    EXPECT_TRUE(foo == expected);
}

UTEST(EnumArray, Encode) {
    auto foo = fcp::S4{{fcp::E::S0,fcp::E::S1,fcp::E::S2,fcp::E::S0}, 5,6};
    auto encoded = foo.encode().GetData();

    std::vector<uint8_t> bytes{0x24,5,6};
    EXPECT_TRUE(encoded == bytes);
}

UTEST(EnumArray, Decode) {
    std::vector<uint8_t> bytes{0x24,5,6};

    auto foo = fcp::S4::Decode(bytes.begin(), bytes.end());
    auto expected = fcp::S4{{fcp::E::S0,fcp::E::S1,fcp::E::S2,fcp::E::S0}, 5, 6};

    EXPECT_TRUE(foo == expected);
}


UTEST(SignedValues, Encode) {
    auto foo = fcp::S5{1,-2,3,-4,5,-6,7,-8,9,-10};
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

UTEST(SignedValues, Decode) {
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

    auto foo = fcp::S5::Decode(bytes.begin(), bytes.end());
    auto expected = fcp::S5{1,-2,3,-4,5,-6,7,-8,9,-10};
    EXPECT_TRUE(foo==expected);
}

UTEST(FloatingPointValues, EncodeSignedAndUnsignedStruct) {
    auto foo = fcp::S6{1.0, 1.0};
    std::vector<std::uint8_t> encoded = foo.encode().GetData();

    std::vector<uint8_t> bytes{
        0x00, 0x00, 0x80, 0x3f,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xF0, 0x3F};


    EXPECT_TRUE(encoded==bytes);
}

UTEST(FloatingPointValues, DecodeSignedAndUnsignedStruct) {
    std::vector<uint8_t> bytes{
        0x00, 0x00, 0x80, 0x3f,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xF0, 0x3F};

    auto foo = fcp::S6::Decode(bytes.begin(), bytes.end());
    auto expected = fcp::S6{1.0, 1.0};

    EXPECT_TRUE(foo==expected);
}

UTEST(BasicStruct, EncodeString) {
    auto s1 = fcp::S7{"hello"};
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

    auto foo = fcp::S7::Decode(bytes.begin(), bytes.end());
    auto expected = fcp::S7{"hello"};

    EXPECT_TRUE(foo==expected);
}

UTEST(DynamicArray, Encode) {
    auto s1 = fcp::S8{{{0,1,2}}};
    std::vector<std::uint8_t> encoded = s1.encode().GetData();

    std::vector<uint8_t> bytes{
        0x03, 0x00, 0x00, 0x00,
        0x00, 0x01, 0x02};


    EXPECT_TRUE(encoded==bytes);
}

UTEST(DynamicArray, Decode) {
    std::vector<uint8_t> bytes{
        0x03, 0x00, 0x00, 0x00,
        0x00, 0x01, 0x02};

    auto foo = fcp::S8::Decode(bytes.begin(), bytes.end());
    auto expected = fcp::S8{{{0,1,2}}};

    EXPECT_TRUE(foo==expected);
}

UTEST(Optional, EncodeOptionalWithValue) {
    auto s1 = fcp::S10{fcp::S10::S1Type{1}};
    std::vector<std::uint8_t> encoded = s1.encode().GetData();

    std::vector<uint8_t> bytes{0x01, 0x1};

    EXPECT_TRUE(encoded==bytes);
}

UTEST(Optional, EncodeOptionalWithNoValue) {
    auto s1 = fcp::S10{fcp::Optional<fcp::Unsigned<std::uint8_t, 8>>::None()};
    std::vector<std::uint8_t> encoded = s1.encode().GetData();

    std::vector<uint8_t> bytes{0x00};

    EXPECT_TRUE(encoded==bytes);
}

UTEST(Optional, DecodeOptionalWithValue) {
    std::vector<uint8_t> bytes{0x01, 0x01};

    auto foo = fcp::S10::Decode(bytes.begin(), bytes.end());
    auto expected = fcp::S10{fcp::S10::S1Type{1}};

    EXPECT_TRUE(foo==expected);
}

UTEST(Optional, DecodeOptionalWithNoValue) {
    std::vector<uint8_t> bytes{0x00};

    auto foo = fcp::S10::Decode(bytes.begin(), bytes.end());
    auto expected = fcp::S10{fcp::Optional<fcp::Unsigned<std::uint8_t, 8>>::None()};

    EXPECT_TRUE(foo==expected);
}
