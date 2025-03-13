#include "fcp.h"
#include <iostream>
#include <utility>
#include <map>
#include <cstdint>

class Proxy {
    public:
        Proxy() {}
    
        void SensorReq() {}

    private:
        void ProcessCanBus() {
             // std::vector<std::uint8_t> input = recv();
             // auto decoded = Decode(input);
             // 
        }


        //std::map<std::pair<std::uint16_t, std::uint16_t>>
};

template<typename T>
void send_request(T input) {
   auto encoded = input.Encode().GetData();

   std::cout << "encoded size: " << encoded.size() << std::endl;

   std::cout << "bytes: ";
   for (auto x: encoded) {
       std::cout << std::hex << (int) x << " ";
   }

   std::cout << std::endl;
}

int main() {
    std::cout << "hello world" << std::endl;

    send_request(fcp::SensorReqInput{
            fcp::ServiceId::SensorService,
            fcp::SensorServiceMethodId::RequestState,
            fcp::SensorReq{fcp::SensorId::Right}}
    );
    return 0;
}
