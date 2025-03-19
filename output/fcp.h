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

#include <vector>
#include <cstdint>
#include <map>
#include <any>
#include <array>
#include <variant>
#include <memory>
#include <string>
#include <sstream>
#include <algorithm>
#include <cstring>
#include <optional>

#include <nlohmann/json.hpp>

#include "buffer.h"
#include "decoders.h"
#include "i_schema.h"

namespace fcp {


using json = nlohmann::json;


class SensorState {
public:
    using UnderlyingType = std::uint8_t;
    static constexpr UnderlyingType Off = 0;
    static constexpr UnderlyingType On = 1;
    static constexpr UnderlyingType Error = 2;

    SensorState(): data_{} {}
    SensorState(UnderlyingType value): data_{value} {}

    static SensorState FromJson(json j) {
        return SensorState{j.get<UnderlyingType>()};
    }

    static SensorState Decode(Buffer& buffer, Endianess endianess=Endianess::Little) {
        UnderlyingType data = buffer.GetWord(GetSize(), false, endianess);
        return data;
    }

    json DecodeJson() const {
        return GetData();
    }

    Buffer Encode(Endianess endianess=Endianess::Little) {
        Buffer buffer{0};
        Encode(buffer, endianess);
        return buffer;
    }

    void Encode(Buffer& buffer, Endianess endianess=Endianess::Little) const {
        buffer.PushWord<UnderlyingType, 1>(data_, endianess);
    }

    static std::size_t GetSize() {
        return 1;
    }

    UnderlyingType GetData() const {
        return data_;
    }

    inline bool operator==(const SensorState& rhs) const {
        return GetData() == rhs.GetData();
    }

    std::string ToString(std::string prefix="") const {
        std::stringstream ss{};

        switch(GetData()) {
        case SensorState::Off:
            return "Off";
        case SensorState::On:
            return "On";
        case SensorState::Error:
            return "Error";
        default:
            return "DecodingError";
        }
    }

private:
    UnderlyingType data_;
};

class SensorId {
public:
    using UnderlyingType = std::uint8_t;
    static constexpr UnderlyingType Left = 0;
    static constexpr UnderlyingType Right = 1;

    SensorId(): data_{} {}
    SensorId(UnderlyingType value): data_{value} {}

    static SensorId FromJson(json j) {
        return SensorId{j.get<UnderlyingType>()};
    }

    static SensorId Decode(Buffer& buffer, Endianess endianess=Endianess::Little) {
        UnderlyingType data = buffer.GetWord(GetSize(), false, endianess);
        return data;
    }

    json DecodeJson() const {
        return GetData();
    }

    Buffer Encode(Endianess endianess=Endianess::Little) {
        Buffer buffer{0};
        Encode(buffer, endianess);
        return buffer;
    }

    void Encode(Buffer& buffer, Endianess endianess=Endianess::Little) const {
        buffer.PushWord<UnderlyingType, 1>(data_, endianess);
    }

    static std::size_t GetSize() {
        return 1;
    }

    UnderlyingType GetData() const {
        return data_;
    }

    inline bool operator==(const SensorId& rhs) const {
        return GetData() == rhs.GetData();
    }

    std::string ToString(std::string prefix="") const {
        std::stringstream ss{};

        switch(GetData()) {
        case SensorId::Left:
            return "Left";
        case SensorId::Right:
            return "Right";
        default:
            return "DecodingError";
        }
    }

private:
    UnderlyingType data_;
};

class ServiceId {
public:
    using UnderlyingType = std::uint8_t;
    static constexpr UnderlyingType SensorService = 0;
    static constexpr UnderlyingType Max = 255;

    ServiceId(): data_{} {}
    ServiceId(UnderlyingType value): data_{value} {}

    static ServiceId FromJson(json j) {
        return ServiceId{j.get<UnderlyingType>()};
    }

    static ServiceId Decode(Buffer& buffer, Endianess endianess=Endianess::Little) {
        UnderlyingType data = buffer.GetWord(GetSize(), false, endianess);
        return data;
    }

    json DecodeJson() const {
        return GetData();
    }

    Buffer Encode(Endianess endianess=Endianess::Little) {
        Buffer buffer{0};
        Encode(buffer, endianess);
        return buffer;
    }

    void Encode(Buffer& buffer, Endianess endianess=Endianess::Little) const {
        buffer.PushWord<UnderlyingType, 8>(data_, endianess);
    }

    static std::size_t GetSize() {
        return 8;
    }

    UnderlyingType GetData() const {
        return data_;
    }

    inline bool operator==(const ServiceId& rhs) const {
        return GetData() == rhs.GetData();
    }

    std::string ToString(std::string prefix="") const {
        std::stringstream ss{};

        switch(GetData()) {
        case ServiceId::SensorService:
            return "SensorService";
        case ServiceId::Max:
            return "Max";
        default:
            return "DecodingError";
        }
    }

private:
    UnderlyingType data_;
};

class SensorServiceMethodId {
public:
    using UnderlyingType = std::uint8_t;
    static constexpr UnderlyingType RequestState = 0;
    static constexpr UnderlyingType GetTemperature = 1;
    static constexpr UnderlyingType Max = 255;

    SensorServiceMethodId(): data_{} {}
    SensorServiceMethodId(UnderlyingType value): data_{value} {}

    static SensorServiceMethodId FromJson(json j) {
        return SensorServiceMethodId{j.get<UnderlyingType>()};
    }

    static SensorServiceMethodId Decode(Buffer& buffer, Endianess endianess=Endianess::Little) {
        UnderlyingType data = buffer.GetWord(GetSize(), false, endianess);
        return data;
    }

    json DecodeJson() const {
        return GetData();
    }

    Buffer Encode(Endianess endianess=Endianess::Little) {
        Buffer buffer{0};
        Encode(buffer, endianess);
        return buffer;
    }

    void Encode(Buffer& buffer, Endianess endianess=Endianess::Little) const {
        buffer.PushWord<UnderlyingType, 8>(data_, endianess);
    }

    static std::size_t GetSize() {
        return 8;
    }

    UnderlyingType GetData() const {
        return data_;
    }

    inline bool operator==(const SensorServiceMethodId& rhs) const {
        return GetData() == rhs.GetData();
    }

    std::string ToString(std::string prefix="") const {
        std::stringstream ss{};

        switch(GetData()) {
        case SensorServiceMethodId::RequestState:
            return "RequestState";
        case SensorServiceMethodId::GetTemperature:
            return "GetTemperature";
        case SensorServiceMethodId::Max:
            return "Max";
        default:
            return "DecodingError";
        }
    }

private:
    UnderlyingType data_;
};


struct Temperature {
    using TemperatureType = Unsigned<std::uint32_t, 32>;
    using TimestampType = Unsigned<std::uint32_t, 32>;

    Temperature():
        temperature_{},
        timestamp_{}
    {}

    Temperature(TemperatureType temperature,TimestampType timestamp):
        temperature_{temperature},
        timestamp_{timestamp}
    {}

    static Temperature FromJson(json j){
        return Temperature {
            TemperatureType::FromJson(j["temperature"]),
            TimestampType::FromJson(j["timestamp"]),
        };
    }

    static Temperature Decode(Buffer& buffer, Endianess endianess=Endianess::Little) {
        auto temperature = TemperatureType::Decode(buffer, endianess);
        auto timestamp = TimestampType::Decode(buffer, endianess);

        return Temperature(temperature,timestamp);
    }

    template<typename Iterator>
    static Temperature Decode(Iterator begin, Iterator end) {
        auto buffer = Buffer{begin, end};
        return Temperature::Decode(buffer);
    }

    json DecodeJson() const {
        json j{};
        j["temperature"] = temperature_.DecodeJson();
        j["timestamp"] = timestamp_.DecodeJson();
        return j;
    }

    Buffer Encode(Endianess endianess=Endianess::Little) {
        Buffer buffer{0};
        Encode(buffer, endianess);
        return buffer;
    }

    void Encode(Buffer& buffer, Endianess endianess=Endianess::Little) const {
        temperature_.Encode(buffer, endianess);
        timestamp_.Encode(buffer, endianess);
    }
    TemperatureType GetTemperature() const {
        return temperature_;
    }
    TimestampType GetTimestamp() const {
        return timestamp_;
    }
    TemperatureType& ViewTemperature() {
        return temperature_;
    }
    TimestampType& ViewTimestamp() {
        return timestamp_;
    }
    inline bool operator==(const Temperature& rhs) const {
        return  temperature_ == rhs.GetTemperature()
        	&& timestamp_ == rhs.GetTimestamp();
    }

    std::string ToString(std::string prefix = "") const {
        std::stringstream ss{};
        auto p = prefix + "\t";
        ss << "Temperature {" << std::endl;
        ss << p << "temperature: " << temperature_.ToString(p) << std::endl;
        ss << p << "timestamp: " << timestamp_.ToString(p) << std::endl;
        ss << prefix << "}" << std::endl;
        return ss.str();
    }

private:
    TemperatureType temperature_;
    TimestampType timestamp_;
};


struct SensorInformation {
    using TemperatureType = Temperature;
    using SensorStateType = SensorState;

    SensorInformation():
        temperature_{},
        sensor_state_{}
    {}

    SensorInformation(TemperatureType temperature,SensorStateType sensor_state):
        temperature_{temperature},
        sensor_state_{sensor_state}
    {}

    static SensorInformation FromJson(json j){
        return SensorInformation {
            TemperatureType::FromJson(j["temperature"]),
            SensorStateType::FromJson(j["sensor_state"]),
        };
    }

    static SensorInformation Decode(Buffer& buffer, Endianess endianess=Endianess::Little) {
        auto temperature = TemperatureType::Decode(buffer, endianess);
        auto sensor_state = SensorStateType::Decode(buffer, endianess);

        return SensorInformation(temperature,sensor_state);
    }

    template<typename Iterator>
    static SensorInformation Decode(Iterator begin, Iterator end) {
        auto buffer = Buffer{begin, end};
        return SensorInformation::Decode(buffer);
    }

    json DecodeJson() const {
        json j{};
        j["temperature"] = temperature_.DecodeJson();
        j["sensor_state"] = sensor_state_.DecodeJson();
        return j;
    }

    Buffer Encode(Endianess endianess=Endianess::Little) {
        Buffer buffer{0};
        Encode(buffer, endianess);
        return buffer;
    }

    void Encode(Buffer& buffer, Endianess endianess=Endianess::Little) const {
        temperature_.Encode(buffer, endianess);
        sensor_state_.Encode(buffer, endianess);
    }
    TemperatureType GetTemperature() const {
        return temperature_;
    }
    SensorStateType GetSensorState() const {
        return sensor_state_;
    }
    TemperatureType& ViewTemperature() {
        return temperature_;
    }
    SensorStateType& ViewSensorState() {
        return sensor_state_;
    }
    inline bool operator==(const SensorInformation& rhs) const {
        return  temperature_ == rhs.GetTemperature()
        	&& sensor_state_ == rhs.GetSensorState();
    }

    std::string ToString(std::string prefix = "") const {
        std::stringstream ss{};
        auto p = prefix + "\t";
        ss << "SensorInformation {" << std::endl;
        ss << p << "temperature: " << temperature_.ToString(p) << std::endl;
        ss << p << "sensor_state: " << sensor_state_.ToString(p) << std::endl;
        ss << prefix << "}" << std::endl;
        return ss.str();
    }

private:
    TemperatureType temperature_;
    SensorStateType sensor_state_;
};


struct SensorReq {
    using SensorIdType = SensorId;

    SensorReq():
        sensor_id_{}
    {}

    SensorReq(SensorIdType sensor_id):
        sensor_id_{sensor_id}
    {}

    static SensorReq FromJson(json j){
        return SensorReq {
            SensorIdType::FromJson(j["sensor_id"]),
        };
    }

    static SensorReq Decode(Buffer& buffer, Endianess endianess=Endianess::Little) {
        auto sensor_id = SensorIdType::Decode(buffer, endianess);

        return SensorReq(sensor_id);
    }

    template<typename Iterator>
    static SensorReq Decode(Iterator begin, Iterator end) {
        auto buffer = Buffer{begin, end};
        return SensorReq::Decode(buffer);
    }

    json DecodeJson() const {
        json j{};
        j["sensor_id"] = sensor_id_.DecodeJson();
        return j;
    }

    Buffer Encode(Endianess endianess=Endianess::Little) {
        Buffer buffer{0};
        Encode(buffer, endianess);
        return buffer;
    }

    void Encode(Buffer& buffer, Endianess endianess=Endianess::Little) const {
        sensor_id_.Encode(buffer, endianess);
    }
    SensorIdType GetSensorId() const {
        return sensor_id_;
    }
    SensorIdType& ViewSensorId() {
        return sensor_id_;
    }
    inline bool operator==(const SensorReq& rhs) const {
        return  sensor_id_ == rhs.GetSensorId();
    }

    std::string ToString(std::string prefix = "") const {
        std::stringstream ss{};
        auto p = prefix + "\t";
        ss << "SensorReq {" << std::endl;
        ss << p << "sensor_id: " << sensor_id_.ToString(p) << std::endl;
        ss << prefix << "}" << std::endl;
        return ss.str();
    }

private:
    SensorIdType sensor_id_;
};


struct SensorreqInput {
    using ServiceIdType = ServiceId;
    using MethodIdType = SensorServiceMethodId;
    using PayloadType = SensorReq;

    SensorreqInput():
        service_id_{},
        method_id_{},
        payload_{}
    {}

    SensorreqInput(ServiceIdType service_id,MethodIdType method_id,PayloadType payload):
        service_id_{service_id},
        method_id_{method_id},
        payload_{payload}
    {}

    static SensorreqInput FromJson(json j){
        return SensorreqInput {
            ServiceIdType::FromJson(j["service_id"]),
            MethodIdType::FromJson(j["method_id"]),
            PayloadType::FromJson(j["payload"]),
        };
    }

    static SensorreqInput Decode(Buffer& buffer, Endianess endianess=Endianess::Little) {
        auto service_id = ServiceIdType::Decode(buffer, endianess);
        auto method_id = MethodIdType::Decode(buffer, endianess);
        auto payload = PayloadType::Decode(buffer, endianess);

        return SensorreqInput(service_id,method_id,payload);
    }

    template<typename Iterator>
    static SensorreqInput Decode(Iterator begin, Iterator end) {
        auto buffer = Buffer{begin, end};
        return SensorreqInput::Decode(buffer);
    }

    json DecodeJson() const {
        json j{};
        j["service_id"] = service_id_.DecodeJson();
        j["method_id"] = method_id_.DecodeJson();
        j["payload"] = payload_.DecodeJson();
        j["__is_method_input"] = true;
        return j;
    }

    Buffer Encode(Endianess endianess=Endianess::Little) {
        Buffer buffer{0};
        Encode(buffer, endianess);
        return buffer;
    }

    void Encode(Buffer& buffer, Endianess endianess=Endianess::Little) const {
        service_id_.Encode(buffer, endianess);
        method_id_.Encode(buffer, endianess);
        payload_.Encode(buffer, endianess);
    }
    ServiceIdType GetServiceId() const {
        return service_id_;
    }
    MethodIdType GetMethodId() const {
        return method_id_;
    }
    PayloadType GetPayload() const {
        return payload_;
    }
    ServiceIdType& ViewServiceId() {
        return service_id_;
    }
    MethodIdType& ViewMethodId() {
        return method_id_;
    }
    PayloadType& ViewPayload() {
        return payload_;
    }
    inline bool operator==(const SensorreqInput& rhs) const {
        return  service_id_ == rhs.GetServiceId()
        	&& method_id_ == rhs.GetMethodId()
        	&& payload_ == rhs.GetPayload();
    }

    std::string ToString(std::string prefix = "") const {
        std::stringstream ss{};
        auto p = prefix + "\t";
        ss << "SensorreqInput {" << std::endl;
        ss << p << "service_id: " << service_id_.ToString(p) << std::endl;
        ss << p << "method_id: " << method_id_.ToString(p) << std::endl;
        ss << p << "payload: " << payload_.ToString(p) << std::endl;
        ss << prefix << "}" << std::endl;
        return ss.str();
    }

private:
    ServiceIdType service_id_;
    MethodIdType method_id_;
    PayloadType payload_;
};


struct SensorinformationOutput {
    using ServiceIdType = ServiceId;
    using MethodIdType = SensorServiceMethodId;
    using PayloadType = SensorInformation;

    SensorinformationOutput():
        service_id_{},
        method_id_{},
        payload_{}
    {}

    SensorinformationOutput(ServiceIdType service_id,MethodIdType method_id,PayloadType payload):
        service_id_{service_id},
        method_id_{method_id},
        payload_{payload}
    {}

    static SensorinformationOutput FromJson(json j){
        return SensorinformationOutput {
            ServiceIdType::FromJson(j["service_id"]),
            MethodIdType::FromJson(j["method_id"]),
            PayloadType::FromJson(j["payload"]),
        };
    }

    static SensorinformationOutput Decode(Buffer& buffer, Endianess endianess=Endianess::Little) {
        auto service_id = ServiceIdType::Decode(buffer, endianess);
        auto method_id = MethodIdType::Decode(buffer, endianess);
        auto payload = PayloadType::Decode(buffer, endianess);

        return SensorinformationOutput(service_id,method_id,payload);
    }

    template<typename Iterator>
    static SensorinformationOutput Decode(Iterator begin, Iterator end) {
        auto buffer = Buffer{begin, end};
        return SensorinformationOutput::Decode(buffer);
    }

    json DecodeJson() const {
        json j{};
        j["service_id"] = service_id_.DecodeJson();
        j["method_id"] = method_id_.DecodeJson();
        j["payload"] = payload_.DecodeJson();
        return j;
    }

    Buffer Encode(Endianess endianess=Endianess::Little) {
        Buffer buffer{0};
        Encode(buffer, endianess);
        return buffer;
    }

    void Encode(Buffer& buffer, Endianess endianess=Endianess::Little) const {
        service_id_.Encode(buffer, endianess);
        method_id_.Encode(buffer, endianess);
        payload_.Encode(buffer, endianess);
    }
    ServiceIdType GetServiceId() const {
        return service_id_;
    }
    MethodIdType GetMethodId() const {
        return method_id_;
    }
    PayloadType GetPayload() const {
        return payload_;
    }
    ServiceIdType& ViewServiceId() {
        return service_id_;
    }
    MethodIdType& ViewMethodId() {
        return method_id_;
    }
    PayloadType& ViewPayload() {
        return payload_;
    }
    inline bool operator==(const SensorinformationOutput& rhs) const {
        return  service_id_ == rhs.GetServiceId()
        	&& method_id_ == rhs.GetMethodId()
        	&& payload_ == rhs.GetPayload();
    }

    std::string ToString(std::string prefix = "") const {
        std::stringstream ss{};
        auto p = prefix + "\t";
        ss << "SensorinformationOutput {" << std::endl;
        ss << p << "service_id: " << service_id_.ToString(p) << std::endl;
        ss << p << "method_id: " << method_id_.ToString(p) << std::endl;
        ss << p << "payload: " << payload_.ToString(p) << std::endl;
        ss << prefix << "}" << std::endl;
        return ss.str();
    }

private:
    ServiceIdType service_id_;
    MethodIdType method_id_;
    PayloadType payload_;
};


struct TemperatureOutput {
    using ServiceIdType = ServiceId;
    using MethodIdType = SensorServiceMethodId;
    using PayloadType = Temperature;

    TemperatureOutput():
        service_id_{},
        method_id_{},
        payload_{}
    {}

    TemperatureOutput(ServiceIdType service_id,MethodIdType method_id,PayloadType payload):
        service_id_{service_id},
        method_id_{method_id},
        payload_{payload}
    {}

    static TemperatureOutput FromJson(json j){
        return TemperatureOutput {
            ServiceIdType::FromJson(j["service_id"]),
            MethodIdType::FromJson(j["method_id"]),
            PayloadType::FromJson(j["payload"]),
        };
    }

    static TemperatureOutput Decode(Buffer& buffer, Endianess endianess=Endianess::Little) {
        auto service_id = ServiceIdType::Decode(buffer, endianess);
        auto method_id = MethodIdType::Decode(buffer, endianess);
        auto payload = PayloadType::Decode(buffer, endianess);

        return TemperatureOutput(service_id,method_id,payload);
    }

    template<typename Iterator>
    static TemperatureOutput Decode(Iterator begin, Iterator end) {
        auto buffer = Buffer{begin, end};
        return TemperatureOutput::Decode(buffer);
    }

    json DecodeJson() const {
        json j{};
        j["service_id"] = service_id_.DecodeJson();
        j["method_id"] = method_id_.DecodeJson();
        j["payload"] = payload_.DecodeJson();
        return j;
    }

    Buffer Encode(Endianess endianess=Endianess::Little) {
        Buffer buffer{0};
        Encode(buffer, endianess);
        return buffer;
    }

    void Encode(Buffer& buffer, Endianess endianess=Endianess::Little) const {
        service_id_.Encode(buffer, endianess);
        method_id_.Encode(buffer, endianess);
        payload_.Encode(buffer, endianess);
    }
    ServiceIdType GetServiceId() const {
        return service_id_;
    }
    MethodIdType GetMethodId() const {
        return method_id_;
    }
    PayloadType GetPayload() const {
        return payload_;
    }
    ServiceIdType& ViewServiceId() {
        return service_id_;
    }
    MethodIdType& ViewMethodId() {
        return method_id_;
    }
    PayloadType& ViewPayload() {
        return payload_;
    }
    inline bool operator==(const TemperatureOutput& rhs) const {
        return  service_id_ == rhs.GetServiceId()
        	&& method_id_ == rhs.GetMethodId()
        	&& payload_ == rhs.GetPayload();
    }

    std::string ToString(std::string prefix = "") const {
        std::stringstream ss{};
        auto p = prefix + "\t";
        ss << "TemperatureOutput {" << std::endl;
        ss << p << "service_id: " << service_id_.ToString(p) << std::endl;
        ss << p << "method_id: " << method_id_.ToString(p) << std::endl;
        ss << p << "payload: " << payload_.ToString(p) << std::endl;
        ss << prefix << "}" << std::endl;
        return ss.str();
    }

private:
    ServiceIdType service_id_;
    MethodIdType method_id_;
    PayloadType payload_;
};


struct StaticSchema: public ISchema
{
    StaticSchema() = default;

    std::optional<json> DecodeJson(std::string name, std::vector<std::uint8_t> data, std::string bus="default") const override {
        auto buffer = Buffer{data.begin(), data.end()};
        if (name == "Temperature" && bus == "default") {
            return Temperature::Decode(buffer).DecodeJson();
        }
        if (name == "SensorInformation" && bus == "default") {
            return SensorInformation::Decode(buffer).DecodeJson();
        }
        if (name == "SensorReq" && bus == "default") {
            return SensorReq::Decode(buffer).DecodeJson();
        }
        if (name == "SensorreqInput" && bus == "default") {
            return SensorreqInput::Decode(buffer).DecodeJson();
        }
        if (name == "SensorinformationOutput" && bus == "default") {
            return SensorinformationOutput::Decode(buffer).DecodeJson();
        }
        if (name == "TemperatureOutput" && bus == "default") {
            return TemperatureOutput::Decode(buffer).DecodeJson();
        }

        return std::nullopt;
    }

    std::optional<std::vector<std::uint8_t>> EncodeJson(std::string msg_name, json j) const override {
        if (msg_name == "Temperature") {
            auto s = Temperature::FromJson(j);
            return s.Encode().GetData();
        }
        if (msg_name == "SensorInformation") {
            auto s = SensorInformation::FromJson(j);
            return s.Encode().GetData();
        }
        if (msg_name == "SensorReq") {
            auto s = SensorReq::FromJson(j);
            return s.Encode().GetData();
        }
        if (msg_name == "SensorreqInput") {
            auto s = SensorreqInput::FromJson(j);
            return s.Encode().GetData();
        }
        if (msg_name == "SensorinformationOutput") {
            auto s = SensorinformationOutput::FromJson(j);
            return s.Encode().GetData();
        }
        if (msg_name == "TemperatureOutput") {
            auto s = TemperatureOutput::FromJson(j);
            return s.Encode().GetData();
        }

        return std::nullopt;
    }
};
} // namespace fcp
