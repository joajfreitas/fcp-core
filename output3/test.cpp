//#include "fcp_can.h"
#include "fcp.h"

#include <iostream>

#include "utest.h"

//UTEST_MAIN()
//
//UTEST(BasicStruct, Decode) {
//    auto foo = fcp::Foo{1,2};
//    auto encoded = foo.encode();
//    
//    for (int i=0; i<2; i++) {
//        std::cout << (int) encoded[i] << std::endl;
//    }
//    std::vector<uint8_t> bytes{0,1,2};
//    EXPECT_TRUE(encoded==bytes);
//}
//
//UTEST(BasicStruct, Encode) {
//    std::vector<uint8_t> bytes{0,1,2};
//
//    auto foo = fcp::Foo::decode<std::vector<uint8_t>::iterator>(bytes.begin());
//    auto expected = fcp::Foo{1,2};
//    std::cout << (int)foo.s2 << std::endl;
//    std::cout << (int)foo.s3 << std::endl;
//    EXPECT_TRUE(foo==expected);
//}

//UTEST(BasicStruct, GetDeviceName) {
//    EXPECT_EQ(fcp::can::Fcp::get_device_name(10), "ecu1");
//}


int main() {
    std::vector<uint8_t> bytes1{0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,100,101};
    fcp::Buffer buffer1{bytes1};

    auto foo = fcp::Foo(buffer1);
    
    std::cout << foo.to_string();

    std::vector<uint8_t> bytes2{0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,100,101,55,56,57,2};
    fcp::Buffer buffer2{bytes2};
    auto bar = fcp::Bar{buffer2};
    
    
    auto buffer3 = bar.encode();
        
    for (const auto& x: buffer3.GetData()) {
        std::cout << (int) x << ",";
    }
    std::cout << std::endl;
        
    std::cout << bar.to_string() << std::endl;

    auto buffer4 = bar.encode();
        
    for (const auto& x: buffer4.GetData()) {
        std::cout << (int) x << ",";
    }
    std::cout << std::endl;
    return 0;
}
