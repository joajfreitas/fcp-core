#include "fcp.h"
#include <iostream>
#include <utility>
#include <map>
#include <cstdint>
#include <optional>
#include <future>
#include <any>

#include <nlohmann/json.hpp>

using namespace std::chrono_literals;

using json = nlohmann::json;

template<typename T>
class MethodResponse {
    public:
        MethodResponse(std::future<json>&& future): future_{std::move(future)} {}

        bool ready() {
            return future_.wait_for(0s) == std::future_status::ready;
        }

        std::optional<T> value() {
            if (ready()) {
                return T::FromJson(future_.get());
            }
            return std::nullopt;
        }

    private:
        std::future<json> future_;
};


class IBusProxy {
    public:
        virtual void Send(std::vector<std::uint8_t>& data, std::string msg_name) = 0;
        virtual std::optional<std::pair<std::vector<std::uint8_t>, std::string>> Recv() = 0;
};

class BusProxy: public IBusProxy {
    public:
        BusProxy(): buffer_{}, msg_name_{""} {}

        void Send(std::vector<std::uint8_t>& data, std::string msg_name) {
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

    struct MethodIds {
        std::uint16_t service_id;
        std::uint16_t method_id;

        bool operator==(const MethodIds &other) const
        { return (service_id == other.service_id
            && method_id == other.method_id);
        }
        bool operator()(const MethodIds& other) const
        { return (service_id == other.service_id
            && method_id == other.method_id);
        }
    };

    template<>
    struct std::hash<MethodIds> {
        std::size_t operator()(const MethodIds& method_id) const
        {
            std::uint32_t x = (static_cast<std::uint32_t>(method_id.service_id) << 16) | method_id.method_id;
            return std::hash<std::uint32_t>{}(x);
        }
    };

class MethodProxy {

    public:
        MethodProxy(IBusProxy& bus_proxy): bus_proxy_{bus_proxy}, static_schema_{fcp::StaticSchema{}}, pending_requests_{} {}

        MethodResponse<fcp::SensorInformation> RequestState(const fcp::SensorReq& sensor_req) {
            // encode sensor_req
            // send to bus
            // register the waiting of the respose
            fcp::SensorReqInput sensor_req_input{fcp::ServiceId::SensorService, fcp::SensorServiceMethodId::RequestState, sensor_req};

            auto encoded = sensor_req_input.Encode();
            std::promise<json> promise;
            std::future<json> future = promise.get_future();
            pending_requests_.insert({MethodIds{fcp::ServiceId::SensorService, fcp::SensorServiceMethodId::RequestState}, std::move(promise)});
            return std::move(future);
        }

        void Step() {
            auto msg = bus_proxy_.Recv();
            auto decoded = static_schema_.DecodeJson(msg->second, msg->first);

            if (!decoded.has_value()) {
                return;
            }

            for (auto& [key, value]: pending_requests_) {
                if (key.service_id == decoded.value()["service_id"] && key.method_id == decoded.value()["method_id"]) {
                    value.set_value(decoded.value()["payload"]);
                    pending_requests_.erase(key);
                    return;
                }
            }
            return;
        }

    private:
        void ProcessCanBus() {
             // std::vector<std::uint8_t> input = recv();
             // auto decoded = Decode(input);
             //
        }

        IBusProxy& bus_proxy_;
        fcp::StaticSchema static_schema_;
        std::unordered_map<MethodIds, std::promise<json>> pending_requests_;
        //std::map<std::pair<std::uint16_t, std::uint16_t>, >
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

    auto bus_proxy = BusProxy{};
    auto proxy = MethodProxy{bus_proxy};

    auto response = proxy.RequestState(fcp::SensorReq{fcp::SensorId::Right});
    if (response.ready()) {
        std::cout << "waiting for response" << std::endl;
    }
    else {
        std::cout << "response ready" << std::endl;
    }
    std::vector<std::uint8_t> buffer{0x00, 0x00, 0x10, 0x00, 0x00, 0x00, 0x05, 0x00, 0x00, 0x00, 0x01};
    bus_proxy.Send(buffer, "SensorInformationOutput");
    proxy.Step();

    if (response.ready()) {
        std::cout << "waiting for response" << std::endl;
    }
    else {
        std::cout << "response ready" << std::endl;
    }

    auto return_value = response.value();
    std::cout << return_value.value().ToString() << std::endl;

    return 0;
}
