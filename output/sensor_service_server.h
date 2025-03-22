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

// Generated using fcp 1.0.0 on 2025-03-19 21:51:29 by joaj@saturn

// DO NOT EDIT

#pragma once

#include "rpc.h"
#include "i_schema.h"
#include "fcp.h"

namespace fcp {
class ISensorServiceImpl {
    public:
        virtual SensorInformation RequestState(const SensorReq& input) = 0;
        virtual Temperature GetTemperature(const SensorReq& input) = 0;
};

template<typename ServiceImpl>
class SensorServiceBroker {
    public:
        SensorServiceBroker(IBusProxy& bus_proxy, const fcp::ISchema& schema, const ServiceImpl& service_impl, std::uint8_t service_id):
            bus_proxy_{bus_proxy},
            schema_{schema},
            service_impl_{service_impl},
            service_id_{service_id}
        {}

        void Step() {
            auto decoded_ = GetDecodedMethod(bus_proxy_.Recv());

            if (!decoded_.has_value()) {
                return;
            }

            auto decoded = decoded_.value();

            auto service_id = decoded["service_id"]. template get<std::uint8_t>();
            auto method_id = decoded["method_id"]. template get<std::uint8_t>();

            if (service_id != service_id_) {
                return;
            }

            if (method_id == SensorServiceMethodId::RequestState) {
                auto input = SensorReq::FromJson(decoded["payload"]);
                auto response_payload = service_impl_.RequestState(input);
                auto response = SensorInformationOutput{service_id_, method_id, response_payload};
                bus_proxy_.Send(response.Encode().GetData(), "SensorInformationOutput");
                return;
            }
            if (method_id == SensorServiceMethodId::GetTemperature) {
                auto input = SensorReq::FromJson(decoded["payload"]);
                auto response_payload = service_impl_.GetTemperature(input);
                auto response = TemperatureOutput{service_id_, method_id, response_payload};
                bus_proxy_.Send(response.Encode().GetData(), "TemperatureOutput");
                return;
            }
            }

    private:
        std::optional<json> GetDecodedMethod(std::optional<std::pair<std::vector<std::uint8_t>, std::string>> msg) {
            if (!msg.has_value()) {
                return std::nullopt;
            }

            auto [data, msg_name] = msg.value();
            auto decoded = schema_.DecodeJson(msg_name, data);
            if (!decoded.has_value()) {
                return std::nullopt;
            }

            if (!decoded.value().contains("__is_method_input")) {
                return std::nullopt;
            }

            return decoded;
        }

        IBusProxy& bus_proxy_;
        const fcp::ISchema& schema_;
        ServiceImpl service_impl_;
        std::uint8_t service_id_;
};

}
