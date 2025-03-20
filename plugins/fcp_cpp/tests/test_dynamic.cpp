// Copyright (c) 2024 the fcp AUTHORS.
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.

#include <gmock/gmock.h>
#include <gtest/gtest.h>

#include "dynamic.h"
#include "fcp.h"
#include <nlohmann/json.hpp>

#include <cstring>

using json = nlohmann::json;

using testing::Eq;
using testing::Optional;

class DynamicSchemaTest : public testing::Test {
public:
    DynamicSchemaTest()
        : schema_{}
    {
        schema_.LoadBinarySchemaFromFile("output.bin");
    }

    fcp::dynamic::DynamicSchema GetSchema()
    {
        return schema_;
    }

private:
    fcp::dynamic::DynamicSchema schema_;
};

TEST_F(DynamicSchemaTest, DecodeSimpleUnsignedStruct)
{
    auto schema = GetSchema();

    auto decoded = schema.DecodeJson("S1", { 1, 2 });

    EXPECT_THAT(decoded, Optional(Eq(json { { "s1", 1 }, { "s2", 2 } })));
}

TEST_F(DynamicSchemaTest, EncodeSimpleUnsignedStruct)
{
    auto schema = GetSchema();

    auto encoded = schema.EncodeJson("S1", { { "s1", 1 }, { "s2", 2 } });

    EXPECT_THAT(encoded, Optional(Eq(std::vector<std::uint8_t> { 1, 2 })));
}

TEST_F(DynamicSchemaTest, DecodeIntegerStruct)
{
    auto schema = GetSchema();

    auto decoded = schema.DecodeJson("S5", { 1, 2, 3, 0, 4, 0, 5, 0, 0, 6, 0, 0, 7, 0, 0, 0, 8, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0 });

    EXPECT_THAT(decoded, Optional(Eq(json { { "s1", 1 }, { "s2", 2 }, { "s3", 3 }, { "s4", 4 }, { "s5", 5 }, { "s6", 6 }, { "s7", 7 }, { "s8", 8 }, { "s9", 9 }, { "s10", 10 } })));
}

TEST_F(DynamicSchemaTest, EncodeIntegerStruct)
{
    auto schema = GetSchema();

    auto encoded = schema.EncodeJson("S5", { { "s1", 1 }, { "s2", 2 }, { "s3", 3 }, { "s4", 4 }, { "s5", 5 }, { "s6", 6 }, { "s7", 7 }, { "s8", 8 }, { "s9", 9 }, { "s10", 10 } });

    EXPECT_THAT(encoded, Optional(Eq(std::vector<std::uint8_t> { 1, 2, 3, 0, 4, 0, 5, 0, 0, 6, 0, 0, 7, 0, 0, 0, 8, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0 })));
}

TEST_F(DynamicSchemaTest, DecodeFloat)
{
    auto schema = GetSchema();

    auto decoded = schema.DecodeJson("S6", { 0, 0, 0x80, 0x3f, 0, 0, 0, 0, 0, 0, 0, 0});

    EXPECT_THAT(decoded, Optional(Eq(json {
        { "s1", 1.0 }, { "s2", 0.0 }})));
}

TEST_F(DynamicSchemaTest, EncodeFloat)
{
    auto schema = GetSchema();

    auto decoded = schema.EncodeJson("S6", json {{ "s1", 1.0 }, { "s2", 0.0 }});

    EXPECT_THAT(decoded, Optional(Eq(std::vector<std::uint8_t>
            { 0, 0, 0x80, 0x3f, 0, 0, 0, 0, 0, 0, 0, 0})));
}

TEST_F(DynamicSchemaTest, DecodeDouble)
{
    auto schema = GetSchema();

    auto decoded = schema.DecodeJson("S6", { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0xf0, 0x3f});

    EXPECT_THAT(decoded, Optional(Eq(json {
        { "s1", 0.0 }, { "s2", 1.0 }})));
}

TEST_F(DynamicSchemaTest, EncodeDouble)
{
    auto schema = GetSchema();

    auto decoded = schema.EncodeJson("S6", json {{ "s1", 0.0 }, { "s2", 1.0 }});

    EXPECT_THAT(decoded, Optional(Eq(std::vector<std::uint8_t>
            { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0xf0, 0x3f})));
}

TEST_F(DynamicSchemaTest, DecodeString)
{
    auto schema = GetSchema();

    auto decoded = schema.DecodeJson("S7", { 5, 0, 0, 0, 'h', 'e', 'l', 'l', 'o' });

    EXPECT_THAT(decoded, Optional(Eq(json { { "s1", std::string { "hello" } } })));
}

TEST_F(DynamicSchemaTest, EncodeString)
{
    auto schema = GetSchema();

    auto encoded = schema.EncodeJson("S7", json{{"s1", "hello"}});

    EXPECT_THAT(encoded, Optional(Eq(std::vector<std::uint8_t>
            { 5, 0, 0, 0, 'h', 'e', 'l', 'l', 'o'})));
}

TEST_F(DynamicSchemaTest, DecodeStaticArray)
{
    auto schema = GetSchema();

    auto decoded = schema.DecodeJson("S3", { 1, 2, 3, 4, 5, 6 });

    EXPECT_THAT(decoded, Optional(Eq(json { { "s1", { 1, 2, 3, 4 } }, { "s2", 5 }, { "s3", 6 } })));
}

TEST_F(DynamicSchemaTest, EncodeStaticArray)
{
    auto schema = GetSchema();

    auto encoded = schema.EncodeJson("S3", json { { "s1", { 1, 2, 3, 4 } }, { "s2", 5 }, { "s3", 6 } });

    EXPECT_THAT(encoded, Optional(Eq(std::vector<std::uint8_t> { 1, 2, 3, 4, 5, 6 })));
}

TEST_F(DynamicSchemaTest, DecodeNestedStruct)
{
    auto schema = GetSchema();

    auto decoded = schema.DecodeJson("S12", { 1, 2 });

    EXPECT_THAT(decoded, Optional(Eq(json { { "s1", { { "s1", 1 }, { "s2", 2 } } } })));
}

TEST_F(DynamicSchemaTest, EncodeNestedStruct)
{
    auto schema = GetSchema();

    auto encoded = schema.EncodeJson("S12", json { { "s1", { { "s1", 1 }, { "s2", 2 } } } });

    EXPECT_THAT(encoded, Optional(Eq(std::vector<std::uint8_t> { 1, 2 })));
}

TEST_F(DynamicSchemaTest, DecodeEnum)
{
    auto schema = GetSchema();

    auto decoded = schema.DecodeJson("S2", { 0 , 1, 2});

    EXPECT_THAT(decoded, Optional(Eq(json { { "s1", 0}, {"s2", 1}, {"s3", "S2" } })));
}

TEST_F(DynamicSchemaTest, EncodeEnum) {
    auto schema = GetSchema();

    auto encoded = schema.EncodeJson("S2", { { "s1", 0 }, { "s2", 1 }, { "s3", "S2" } });

    EXPECT_THAT(encoded, Optional(Eq(std::vector<std::uint8_t> { 0, 1, 2 })));
}

TEST_F(DynamicSchemaTest, DecodeDynamicArray)
{
    auto schema = GetSchema();

    auto decoded = schema.DecodeJson("S8", { 4, 0, 0, 0, 1, 2, 3, 4 });

    EXPECT_THAT(decoded, Optional(Eq(json { { "s1", { 1, 2, 3, 4 } }})));
}

TEST_F(DynamicSchemaTest, EncodeDynamicArray)
{
    auto schema = GetSchema();

    auto encoded = schema.EncodeJson("S8", json { { "s1", { 1, 2, 3, 4 } }});

    EXPECT_THAT(encoded, Optional(Eq(std::vector<std::uint8_t>{ 4, 0, 0, 0, 1, 2, 3, 4 })));
}

TEST_F(DynamicSchemaTest, DecodeOptional) {
    auto schema = GetSchema();

    auto decoded = schema.DecodeJson("S10", { 1, 1 });

    EXPECT_THAT(decoded, Optional(Eq(json { { "s1", 1 } })));
}

TEST_F(DynamicSchemaTest, EncodeOptional) {
    auto schema = GetSchema();

    auto encoded = schema.EncodeJson("S10", json { { "s1", 1 } });

    EXPECT_THAT(encoded, Optional(Eq(std::vector<std::uint8_t>{ 1, 1 })));
}
