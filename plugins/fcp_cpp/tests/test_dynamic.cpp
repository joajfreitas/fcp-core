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
#include "json.h"
#include "dynamic_rpc.h"

#include <cstring>


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

    EXPECT_THAT(decoded, Optional(Eq(std::map<std::string, json> { { "s1", 1ULL }, { "s2", 2ULL } })));
}

TEST_F(DynamicSchemaTest, EncodeSimpleUnsignedStruct)
{
    auto schema = GetSchema();

    auto encoded = schema.EncodeJson("S1", std::map<std::string, json>{ { "s1", 1ULL }, { "s2", 2ULL } });

    EXPECT_THAT(encoded, Optional(Eq(std::vector<std::uint8_t> { 1, 2 })));
}

TEST_F(DynamicSchemaTest, DecodeIntegerStruct)
{
    auto schema = GetSchema();

    auto decoded = schema.DecodeJson("S5", { 1, 2, 3, 0, 4, 0, 5, 0, 0, 6, 0, 0, 7, 0, 0, 0, 8, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0 });

    auto xs = rva::get<std::map<std::string, json>>(decoded.value());
    for (const auto& [key, _] : xs) {
        std::cout << key << std::endl;
    }

        std::cout << "s1: " << rva::get<std::uint64_t>(xs["s1"]) << std::endl;
        std::cout << "alternative: " << rva::holds_alternative<std::uint64_t>(xs["s2"]) << std::endl;
        std::cout << "s2: " << rva::get<std::int64_t>(xs["s2"]) << std::endl;
        std::cout << "s3: " << rva::get<std::uint64_t>(xs["s3"]) << std::endl;
        std::cout << "s4: " << rva::get<std::int64_t>(xs["s4"]) << std::endl;
        std::cout << "s5: " << rva::get<std::uint64_t>(xs["s5"]) << std::endl;
        std::cout << "s6: " << rva::get<std::int64_t>(xs["s6"]) << std::endl;
        std::cout << "s7: " << rva::get<std::uint64_t>(xs["s7"]) << std::endl;
        std::cout << "s8: " << rva::get<std::int64_t>(xs["s8"]) << std::endl;
        std::cout << "s9: " << rva::get<std::uint64_t>(xs["s9"]) << std::endl;
        std::cout << "s10: " << rva::get<std::int64_t>(xs["s10"]) << std::endl;

    EXPECT_THAT(decoded, Optional(Eq(json { std::map<std::string, json>{{ "s1", 1ULL }, { "s2", 2LL }, { "s3", 3ULL }, { "s4", 4LL }, { "s5", 5ULL }, { "s6", 6LL }, { "s7", 7ULL }, { "s8", 8LL }, { "s9", 9ULL }, { "s10", 10LL } }})));
}

TEST_F(DynamicSchemaTest, EncodeIntegerStruct)
{
    auto schema = GetSchema();

    auto encoded = schema.EncodeJson("S5", json{ std::map<std::string, json>{{ "s1", 1ULL }, { "s2", 2LL }, { "s3", 3ULL }, { "s4", 4LL }, { "s5", 5ULL }, { "s6", 6LL }, { "s7", 7ULL }, { "s8", 8LL }, { "s9", 9ULL }, { "s10", 10LL } }});

    EXPECT_THAT(encoded, Optional(Eq(std::vector<std::uint8_t> { 1, 2, 3, 0, 4, 0, 5, 0, 0, 6, 0, 0, 7, 0, 0, 0, 8, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0 })));
}

TEST_F(DynamicSchemaTest, DecodeFloat)
{
    auto schema = GetSchema();

    auto decoded = schema.DecodeJson("S6", { 0, 0, 0x80, 0x3f, 0, 0, 0, 0, 0, 0, 0, 0});

    EXPECT_THAT(decoded, Optional(Eq(std::map<std::string, json> {
        { "s1", 1.0 }, { "s2", 0.0 }})));
}

TEST_F(DynamicSchemaTest, EncodeFloat)
{
    auto schema = GetSchema();

    auto decoded = schema.EncodeJson("S6", json {std::map<std::string, json>{{ "s1", 1.0 }, { "s2", 0.0 }}});

    EXPECT_THAT(decoded, Optional(Eq(std::vector<std::uint8_t>
            { 0, 0, 0x80, 0x3f, 0, 0, 0, 0, 0, 0, 0, 0})));
}

TEST_F(DynamicSchemaTest, DecodeDouble)
{
    auto schema = GetSchema();

    auto decoded = schema.DecodeJson("S6", { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0xf0, 0x3f});

    EXPECT_THAT(decoded, Optional(Eq(json {
                    std::map<std::string, json>{{ "s1", 0.0 }, { "s2", 1.0 }}})));
}

TEST_F(DynamicSchemaTest, EncodeDouble)
{
    auto schema = GetSchema();

    auto decoded = schema.EncodeJson("S6", json {std::map<std::string, json>{{ "s1", 0.0 }, { "s2", 1.0 }}});

    EXPECT_THAT(decoded, Optional(Eq(std::vector<std::uint8_t>
            { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0xf0, 0x3f})));
}

TEST_F(DynamicSchemaTest, DecodeString)
{
    auto schema = GetSchema();

    auto decoded = schema.DecodeJson("S7", { 5, 0, 0, 0, 'h', 'e', 'l', 'l', 'o' });

    EXPECT_THAT(decoded, Optional(Eq(json { std::map<std::string, json>{{ "s1", std::string { "hello" } }} })));
}

TEST_F(DynamicSchemaTest, EncodeString)
{
    auto schema = GetSchema();

    auto encoded = schema.EncodeJson("S7", std::map<std::string, json>{{"s1", "hello"}});

    EXPECT_THAT(encoded, Optional(Eq(std::vector<std::uint8_t>
            { 5, 0, 0, 0, 'h', 'e', 'l', 'l', 'o'})));
}

TEST_F(DynamicSchemaTest, DecodeStaticArray)
{
    auto schema = GetSchema();

    auto decoded = schema.DecodeJson("S3", { 1, 2, 3, 4, 5, 6 });

    EXPECT_THAT(decoded, Optional(Eq(json { std::map<std::string, json>{{ "s1", json{std::vector<json>{ 1ULL, 2ULL, 3ULL, 4ULL } }}, { "s2", 5ULL }, { "s3", 6ULL }} })));
}

TEST_F(DynamicSchemaTest, EncodeStaticArray)
{
    auto schema = GetSchema();

    auto encoded = schema.EncodeJson("S3", json { std::map<std::string, json>{{ "s1", std::vector<json>{ 1ULL, 2ULL, 3ULL, 4ULL } }, { "s2", 5ULL }, { "s3", 6ULL } }});

    EXPECT_THAT(encoded, Optional(Eq(std::vector<std::uint8_t> { 1, 2, 3, 4, 5, 6 })));
}

TEST_F(DynamicSchemaTest, DecodeNestedStruct)
{
    auto schema = GetSchema();

    auto decoded = schema.DecodeJson("S12", {1, 2});

    EXPECT_THAT(decoded, Optional(Eq(json{std::map<std::string, json>{{"s1", json{std::map<std::string, json>{{"s1", 1ULL}, {"s2", 2ULL}}}}}})));
}

TEST_F(DynamicSchemaTest, EncodeNestedStruct)
{
    auto schema = GetSchema();

    auto encoded = schema.EncodeJson("S12", json { std::map<std::string, json>{{ "s1", std::map<std::string, json>{ { "s1", 1ULL }, { "s2", 2ULL } } } }});

    EXPECT_THAT(encoded, Optional(Eq(std::vector<std::uint8_t> { 1, 2 })));
}

TEST_F(DynamicSchemaTest, DecodeEnum)
{
    auto schema = GetSchema();

    auto decoded = schema.DecodeJson("S2", { 0, 1, 2});

    EXPECT_THAT(decoded, Optional(Eq(json { std::map<std::string, json>{{ "s1", 0ULL}, {"s2", 1ULL}, {"s3", "S2" } }})));
}

TEST_F(DynamicSchemaTest, EncodeEnum) {
    auto schema = GetSchema();

    auto encoded = schema.EncodeJson("S2", json{ std::map<std::string, json>{{ "s1", 0ULL }, { "s2", 1ULL }, { "s3", "S2" } }});

    EXPECT_THAT(encoded, Optional(Eq(std::vector<std::uint8_t> { 0, 1, 2 })));
}

TEST_F(DynamicSchemaTest, DecodeDynamicArray)
{
    auto schema = GetSchema();

    auto decoded = schema.DecodeJson("S8", { 4, 0, 0, 0, 1, 2, 3, 4 });

    EXPECT_THAT(decoded, Optional(Eq(json { std::map<std::string, json>{{ "s1", std::vector<json>{ 1ULL, 2ULL, 3ULL, 4ULL }}}})));
}

TEST_F(DynamicSchemaTest, EncodeDynamicArray)
{
    auto schema = GetSchema();

    auto encoded = schema.EncodeJson("S8", std::map<std::string, json> { { "s1", std::vector<json>{ 1ULL, 2ULL, 3ULL, 4ULL } }});

    EXPECT_THAT(encoded, Optional(Eq(std::vector<std::uint8_t>{ 4, 0, 0, 0, 1, 2, 3, 4 })));
}

TEST_F(DynamicSchemaTest, DecodeOptional) {
    auto schema = GetSchema();

    auto decoded = schema.DecodeJson("S10", { 1, 1 });

    EXPECT_THAT(decoded, Optional(Eq(std::map<std::string, json>{{ "s1", 1ULL }})));
}

TEST_F(DynamicSchemaTest, EncodeOptional) {
    auto schema = GetSchema();

    auto encoded = schema.EncodeJson("S10", std::map<std::string, json>{{ "s1", 1ULL }});

    EXPECT_THAT(encoded, Optional(Eq(std::vector<std::uint8_t>{ 1, 1 })));
}


class MockedBusProxy: public fcp::IBusProxy {
    public:
        MOCK_METHOD(
                void,
                Send,
                (std::string msg_name, const json& data),
                (override));

        MOCK_METHOD(
                (std::optional<std::pair<std::string, json>>),
                Recv,
                (),
                (override));
};

TEST_F(DynamicSchemaTest, Method1Response) {
    auto bus = MockedBusProxy{};
    fcp::rpc::DynamicRpcServer server{GetSchema(), bus};

    EXPECT_CALL(bus, Recv()).WillRepeatedly(testing::Return(std::make_pair("S2Input", std::map<std::string, json>{
        {"service_id", 0ULL},
        {"method_id", 0ULL},
        {"payload", std::map<std::string, json>{{"s1", 1ULL}, {"s2", 2ULL}, {"s3", "S2"}}}
    })));

    EXPECT_CALL(bus, Send(testing::Eq("S3Output"),
        testing::Eq(std::map<std::string, json>{
            {"service_id", 0ULL},
            {"method_id", 0ULL},
            {"payload", std::map<std::string, json>{{"s1", std::vector<json>{0, 1, 2, 3}}, {"s2", 4}, {"s3", 5}}}
        })))
    .Times(testing::Exactly(1));

    server.RegisterHandler(0x00, 0x00, "S3Output", [](const json& input) -> json {
        return json{std::map<std::string, json>{{"s1", std::vector<json>{0,1,2,3}}, {"s2", 4}, {"s3", 5}}};
    });

    server.Step();
}
