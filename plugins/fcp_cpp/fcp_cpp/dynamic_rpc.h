// Copyright (c) 2025 the fcp AUTHORS.
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

#pragma once

#include "functional"
#include "i_schema.h"
#include "json.h"
#include "rpc.h"
#include <map>

namespace fcp {
namespace rpc {
class DynamicRpcServer {
public:
  DynamicRpcServer(IBusProxy &bus_proxy)
      : bus_proxy_{bus_proxy}, handlers_{} {}

  void RegisterHandler(std::uint8_t service_id, std::uint8_t method_id,
                       std::string output_type,
                       std::function<json(const json &)> handler) {
    handlers_[method_id] = std::make_pair(output_type, handler);
  }

  void Step() {
    auto msg = bus_proxy_.Recv();

    std::cout << "has value: " << msg.has_value() << std::endl;
    if (!msg.has_value()) {
      return;
    }

    auto decoded = rva::get<std::map<std::string, json>>(msg.value().second);

    auto service_id = rva::get<std::uint64_t>(decoded["service_id"]);
    auto method_id = rva::get<std::uint64_t>(decoded["method_id"]);

    auto id = (service_id << 8) | method_id;

    if (!handlers_.contains(id)) {
      return;
    }

    auto result = handlers_[id].second(decoded["payload"]);

    auto response = std::map<std::string, json>{
        {"service_id", static_cast<std::uint64_t>(service_id)},
        {"method_id", static_cast<std::uint64_t>(method_id)},
        {"payload", result}};

    bus_proxy_.Send(handlers_[id].first, response);
  }

private:
  IBusProxy &bus_proxy_;
  std::map<std::uint16_t,
           std::pair<std::string, std::function<json(const json &)>>>
      handlers_;
};

class DynamicRpcClient {
    public:
    DynamicRpcClient(IBusProxy &bus_proxy)
        : bus_proxy_{bus_proxy}, pending_requests_{} {}

    std::future<json> Request(std::uint8_t service_id, std::uint8_t method_id, std::string input_type, json input) {
        auto id = (service_id << 8) | method_id;

        std::promise<json> promise;
        std::future<json> future = promise.get_future();
        pending_requests_.insert({id, std::move(promise)});

        auto request = std::map<std::string, json>{
            {"service_id", static_cast<std::uint64_t>(service_id)},
            {"method_id", static_cast<std::uint64_t>(method_id)},
            {"payload", input}};

        bus_proxy_.Send(input_type, request);

        return future;
    }

    void Step() {
        auto msg = bus_proxy_.Recv();

        if (!msg.has_value()) {
            return;
        }

        auto decoded = rva::get<std::map<std::string, json>>(msg.value().second);
        auto service_id = rva::get<std::uint64_t>(decoded["service_id"]);
        auto method_id = rva::get<std::uint64_t>(decoded["method_id"]);

        for (auto& [key, value]: pending_requests_) {
            if (key == ((service_id << 8) | method_id)) {
                value.set_value(decoded["payload"]);
                pending_requests_.erase(key);
                return;
            }
        }
    }

    private:
    IBusProxy &bus_proxy_;
    std::unordered_map<std::uint16_t, std::promise<json>> pending_requests_;
};
} // namespace rpc
} // namespace fcp
