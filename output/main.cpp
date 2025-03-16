#include "fcp.h"
#include <iostream>
#include <utility>
#include <map>
#include <cstdint>
#include <optional>
#include <future>
#include <any>
#include <thread>

#include <nlohmann/json.hpp>

using namespace std::chrono_literals;

using json = nlohmann::json;

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

class IBusProxy {
    public:
        virtual void Send(const std::vector<std::uint8_t>& data, std::string msg_name) = 0;
        virtual std::optional<std::pair<std::vector<std::uint8_t>, std::string>> Recv() = 0;
};

class BusProxy: public IBusProxy {
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

class ISensorServiceImpl {
    public:
        virtual fcp::SensorInformation RequestState(const fcp::SensorReq& sensor_req) = 0;
        virtual fcp::Temperature GetTemperature(const fcp::SensorReq& sensor_req) = 0;
};

class SensorServiceImpl: public ISensorServiceImpl {
    public:
        fcp::SensorInformation RequestState(const fcp::SensorReq& sensor_req) {
            return fcp::SensorInformation{fcp::Temperature{16, 5}, fcp::SensorState::On};
        }
        fcp::Temperature GetTemperature(const fcp::SensorReq& sensor_req) {
            return fcp::Temperature{16, 5};
        }
};


template<typename ServiceImpl>
class ServerBroker {
    public:
        ServerBroker(IBusProxy& bus_proxy, const fcp::StaticSchema& static_schema, ServiceImpl& service_impl, std::uint8_t service_id): bus_proxy_{bus_proxy}, static_schema_{static_schema}, service_impl_{service_impl}, service_id_{service_id} {}

        void Step() {
            auto msg = bus_proxy_.Recv();
            if (!msg.has_value()) {
                return;
            }

            auto [data, msg_name] = msg.value();
            auto decoded_ = static_schema_.DecodeJson(msg_name, data);
            if (!decoded_.has_value()) {
                return;
            }

            auto decoded = decoded_.value();

            if (!decoded.contains("__is_method_input")) {
                return;
            }

            auto service_id = decoded["service_id"].get<std::uint8_t>();
            auto method_id = decoded["method_id"].get<std::uint8_t>();


            if (service_id != fcp::ServiceId::SensorService) {
                return;
            }
            if (method_id == fcp::SensorServiceMethodId::RequestState) {
                auto sensor_req = fcp::SensorReq::FromJson(decoded["payload"]);
                auto request_state_payload = service_impl_.RequestState(sensor_req);
                auto response = fcp::SensorInformationOutput{service_id_, method_id, request_state_payload};
                bus_proxy_.Send(response.Encode().GetData(), "SensorInformationOutput");
            }
        }

    private:
        IBusProxy& bus_proxy_;
        fcp::StaticSchema static_schema_;
        ServiceImpl service_impl_;
        std::uint8_t service_id_;

};

template<typename T>
class MethodResponse {
    public:
        MethodResponse(std::future<json>&& future): future_{std::move(future)}, requested_at_time_{std::chrono::system_clock::now()} {}

        std::chrono::nanoseconds age() {
            return std::chrono::system_clock::now() - requested_at_time_;
        }
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
        std::chrono::time_point<std::chrono::system_clock> requested_at_time_;

};

class MethodProxy {

    public:
        MethodProxy(IBusProxy& bus_proxy): bus_proxy_{bus_proxy}, static_schema_{fcp::StaticSchema{}}, pending_requests_{} {}

        template<typename Input, typename Output>
        MethodResponse<typename Output::PayloadType> HandleMethod(const typename Input::PayloadType& input, std::uint8_t service_id, std::uint8_t method_id) {
            Input input_req{service_id, method_id, input};
            bus_proxy_.Send(input_req.Encode().GetData(), "SensorReqInput");

            std::promise<json> promise;
            std::future<json> future = promise.get_future();
            pending_requests_.insert({MethodIds{service_id, method_id}, std::move(promise)});
            return future;
        }

        MethodResponse<fcp::SensorInformation> RequestState(const fcp::SensorReq& sensor_req) {
            return HandleMethod<fcp::SensorReqInput, fcp::SensorInformationOutput>(sensor_req, fcp::ServiceId::SensorService, fcp::SensorServiceMethodId::RequestState);
        }

        void Step() {
            auto msg = bus_proxy_.Recv();
            if (!msg.has_value()) {
                return;
            }
            auto decoded = static_schema_.DecodeJson(msg.value().second, msg.value().first);

            if (!decoded.has_value()) {
                return;
            }

            auto service_id = decoded.value()["service_id"].get<std::uint8_t>();
            auto method_id = decoded.value()["method_id"].get<std::uint8_t>();
            for (auto& [key, value]: pending_requests_) {
                if (key.service_id == service_id && key.method_id == method_id) {
                    value.set_value(decoded.value()["payload"]);
                    pending_requests_.erase(key);
                    return;
                }
            }
            return;
        }

    private:
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

    auto sensor_service_impl = SensorServiceImpl{};
    auto server_broker = ServerBroker<SensorServiceImpl>{bus_proxy, fcp::StaticSchema{}, sensor_service_impl, fcp::ServiceId::SensorService};

    auto response = proxy.RequestState(fcp::SensorReq{fcp::SensorId::Right});
    std::cout << response.age().count() << std::endl;
    if (response.ready()) {
        std::cout << "waiting for response" << std::endl;
    }
    else {
        std::cout << "response ready" << std::endl;
    }
    server_broker.Step();
    proxy.Step();


    auto return_value = response.value();
    std::cout << return_value.value().ToString() << std::endl;

    return 0;
}
