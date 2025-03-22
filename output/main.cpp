#include "fcp.h"
#include <iostream>
#include <utility>
#include <cstdint>

#include "rpc.h"
#include "sensor_service_client.h"
#include "sensor_service_server.h"

#include <nlohmann/json.hpp>

using namespace std::chrono_literals;

using json = nlohmann::json;

class BusProxy: public fcp::IBusProxy {
    public:
        BusProxy(): buffer_{}, msg_name_{""} {}

        void Send(const std::vector<std::uint8_t>& data, std::string msg_name) {
            buffer_ = data;
            msg_name_ = msg_name;
        }

        std::optional<std::pair<std::vector<std::uint8_t>, std::string>> Recv() {
            return {{buffer_, msg_name_}};
        }

    private:
        std::vector<std::uint8_t> buffer_;
        std::string msg_name_;
};


class SensorServiceImpl: public fcp::ISensorServiceImpl {
    public:
        fcp::SensorInformation RequestState(const fcp::SensorReq& sensor_req) override {
            return fcp::SensorInformation{fcp::Temperature{16, 5}, fcp::SensorState::On};
        }
        fcp::Temperature GetTemperature(const fcp::SensorReq& sensor_req) override {
            return fcp::Temperature{16, 5};
        }
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
    auto schema = fcp::StaticSchema{};
    auto bus_proxy = BusProxy{};
    auto proxy = fcp::SensorServiceProxy{bus_proxy, schema};

    auto sensor_service_impl = SensorServiceImpl{};
    auto server_broker = fcp::SensorServiceBroker<SensorServiceImpl>{bus_proxy, schema, sensor_service_impl, fcp::ServiceId::SensorService};

    auto response = proxy.RequestState(fcp::SensorReq{fcp::SensorId::Right});
    std::cout << response.age().count() << std::endl;
    if (response.ready()) {
        std::cout << "response ready" << std::endl;
    }
    else {
        std::cout << "waiting for response" << std::endl;
    }
    server_broker.Step();
    proxy.Step();

    auto return_value = response.value();
    std::cout << return_value.value().ToString() << std::endl;

    return 0;
}
