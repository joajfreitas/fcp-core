#include "fcp.h"
#include "fcp_can.h"

#include <gtest/gtest.h>
#include <gmock/gmock.h>


TEST(BasicStruct, EncodeSimpleUnsignedStruct) {
    auto foo = fcp::S1{1,2};
    auto encoded = foo.Encode().GetData();

    std::vector<uint8_t> bytes{1,2};
    EXPECT_THAT(encoded,bytes);
}

TEST(BasicStruct, DecodeSimpleUnsignedStruct) {
    std::vector<uint8_t> bytes{1,2};

    auto foo = fcp::S1::Decode(bytes.begin(), bytes.end());
    auto expected = fcp::S1{1,2};
    EXPECT_THAT(foo,expected);
}

TEST(NestedEnum, Encode) {
    auto foo = fcp::S2{1,2,fcp::E::S1};
    auto encoded = foo.Encode().GetData();

    std::vector<uint8_t> bytes{1,2,1};
    EXPECT_THAT(encoded,bytes);
}

TEST(NestedEnum,Decode) {
    std::vector<uint8_t> bytes{1,2,1};

    auto foo = fcp::S2::Decode(bytes.begin(), bytes.end());
    auto expected = fcp::S2{1,2, fcp::E::S1};
    EXPECT_THAT(foo,expected);
}

TEST(SimpleArray, Encode) {
    auto foo = fcp::S3{{1,2,3,4}, 5,6};
    auto encoded = foo.Encode().GetData();

    std::vector<uint8_t> bytes{1,2,3,4,5,6};
    EXPECT_THAT(encoded,bytes);
}

TEST(SimpleArray, Decode) {
    std::vector<uint8_t> bytes{1,2,3,4,5,6};

    auto foo = fcp::S3::Decode(bytes.begin(), bytes.end());
    auto expected = fcp::S3{{1,2,3,4}, 5, 6};
    EXPECT_THAT(foo,expected);
}

TEST(EnumArray, Encode) {
    auto foo = fcp::S4{{fcp::E::S0,fcp::E::S1,fcp::E::S2,fcp::E::S0}, 5,6};
    auto encoded = foo.Encode().GetData();

    std::vector<uint8_t> bytes{0x24,5,6};
    EXPECT_THAT(encoded,bytes);
}

TEST(EnumArray, Decode) {
    std::vector<uint8_t> bytes{0x24,5,6};

    auto foo = fcp::S4::Decode(bytes.begin(), bytes.end());
    auto expected = fcp::S4{{fcp::E::S0,fcp::E::S1,fcp::E::S2,fcp::E::S0}, 5, 6};
    EXPECT_THAT(foo,expected);
}

TEST(SignedValues, Encode) {
    auto foo = fcp::S5{1,-2,3,-4,5,-6,7,-8,9,-10};
    std::vector<std::uint8_t> encoded = foo.Encode().GetData();

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

    EXPECT_THAT(encoded,bytes);
}

TEST(SignedValues, Decode) {
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
    EXPECT_THAT(foo,expected);
}

TEST(FloatingPointValues, EncodeSignedAndUnsignedStruct) {
    auto foo = fcp::S6{1.0, 1.0};
    std::vector<std::uint8_t> encoded = foo.Encode().GetData();

    std::vector<uint8_t> bytes{
        0x00, 0x00, 0x80, 0x3f,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xF0, 0x3F};

    EXPECT_THAT(encoded,bytes);
}

TEST(FloatingPointValues, DecodeSignedAndUnsignedStruct) {
    std::vector<uint8_t> bytes{
        0x00, 0x00, 0x80, 0x3f,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xF0, 0x3F};

    auto foo = fcp::S6::Decode(bytes.begin(), bytes.end());
    auto expected = fcp::S6{1.0, 1.0};
    EXPECT_THAT(foo,expected);
}

TEST(BasicStruct, EncodeString) {
    auto s1 = fcp::S7{"hello"};
    std::vector<std::uint8_t> encoded = s1.Encode().GetData();

    std::vector<uint8_t> bytes{
        0x05, 0x00, 0x00, 0x00,
        0x68, 0x65, 0x6c, 0x6c, 0x6f};

    EXPECT_THAT(encoded,bytes);
}

TEST(BasicStruct, DecodeString) {
    std::vector<uint8_t> bytes{
        0x05, 0x00, 0x00, 0x00,
        0x68, 0x65, 0x6c, 0x6c, 0x6f};

    auto foo = fcp::S7::Decode(bytes.begin(), bytes.end());
    auto expected = fcp::S7{"hello"};
    EXPECT_THAT(foo,expected);
}

TEST(DynamicArray, Encode) {
    auto s1 = fcp::S8{{{0,1,2}}};
    std::vector<std::uint8_t> encoded = s1.Encode().GetData();

    std::vector<uint8_t> bytes{
        0x03, 0x00, 0x00, 0x00,
        0x00, 0x01, 0x02};

    EXPECT_THAT(encoded,bytes);
}

TEST(DynamicArray, Decode) {
    std::vector<uint8_t> bytes{
        0x03, 0x00, 0x00, 0x00,
        0x00, 0x01, 0x02};

    auto foo = fcp::S8::Decode(bytes.begin(), bytes.end());
    auto expected = fcp::S8{{{0,1,2}}};
    EXPECT_THAT(foo,expected);
}

TEST(Optional, EncodeOptionalWithValue) {
    auto s1 = fcp::S10{fcp::S10::S1Type{1}};
    std::vector<std::uint8_t> encoded = s1.Encode().GetData();

    std::vector<uint8_t> bytes{0x01, 0x1};

    EXPECT_THAT(encoded,bytes);
}

TEST(Optional, EncodeOptionalWithNoValue) {
    auto s1 = fcp::S10{fcp::Optional<fcp::Unsigned<std::uint8_t, 8>>::None()};
    std::vector<std::uint8_t> encoded = s1.Encode().GetData();

    std::vector<uint8_t> bytes{0x00};

    EXPECT_THAT(encoded,bytes);
}

TEST(Optional, DecodeOptionalWithValue) {
    std::vector<uint8_t> bytes{0x01, 0x01};

    auto foo = fcp::S10::Decode(bytes.begin(), bytes.end());
    auto expected = fcp::S10{fcp::S10::S1Type{1}};
    EXPECT_THAT(foo,expected);
}

TEST(Optional, DecodeOptionalWithNoValue) {
    std::vector<uint8_t> bytes{0x00};

    auto foo = fcp::S10::Decode(bytes.begin(), bytes.end());
    auto expected = fcp::S10{fcp::Optional<fcp::Unsigned<std::uint8_t, 8>>::None()};
    EXPECT_THAT(foo,expected);
}

TEST(BigEndian16Bit, Decode) {
    std::vector<uint8_t> bytes{0x01, 0x02};

    auto s11 = fcp::can::S11::Decode(bytes.begin(), bytes.end());
    auto expected = fcp::can::S11{0x102};

    EXPECT_THAT(s11,expected);
}
