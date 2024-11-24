#include <iostream>

//#include "fcp_can.h"
#include "fcp.h"

#include "utest.h"

UTEST_MAIN()

UTEST(BasicStruct, EncodeString) {
    auto s1 = fcp::S1{"hello"};
    auto encoded = s1.encode();

    std::cout << encoded.to_string() << std::endl;

    std::vector<uint8_t> bytes{
        0x00, 0x00, 0x00, 0x05,
        0x68, 0x65, 0x6c, 0x6c, 0x6f};


    EXPECT_TRUE(encoded.GetData()==bytes);
}

//UTEST(BasicStruct, DecodeString) {
//    std::vector<uint8_t> bytes{
//        0x00, 0x00, 0x80, 0x3f,
//        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xF0, 0x3F};
//
//    auto foo = fcp::S1::Decode(bytes.begin(), bytes.end());
//    auto expected = fcp::S1{1.0, 1.0};
//
//    EXPECT_TRUE(foo==expected);
//}
