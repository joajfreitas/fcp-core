//#include "fcp_can.h"
#include "fcp.h"

#include <iostream>

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
