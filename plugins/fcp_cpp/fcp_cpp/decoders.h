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

// Generated using fcp {{version}} on {{date}} by {{user}}@{{hostname}}

// DO NOT EDIT

#pragma once

#include <nlohmann/json.hpp>
#
#include "buffer.h"

namespace fcp {

using json = nlohmann::json;

template<typename UnderlyingType, std::size_t BitSize>
class Unsigned {
public:
    Unsigned(): data_{0} {}
    Unsigned(UnderlyingType value): data_{value} {}

    static Unsigned FromJson(json j) {
        return Unsigned(j.get<UnderlyingType>());
    }

    static Unsigned Decode(Buffer& buffer, Endianess endianess=Endianess::Little) {
        auto word = buffer.GetWord(BitSize, false, endianess);
        return Unsigned(static_cast<UnderlyingType>(word));
    }

    json DecodeJson() const {
        return GetData();
    }

    void Encode(Buffer& buffer, Endianess endianess=Endianess::Little) const {
        buffer.PushWord<UnderlyingType, BitSize>(data_, endianess) ;
    }

    UnderlyingType GetData() const {
        return data_;
    }

    inline bool operator==(const Unsigned& rhs) const
    {
        return GetData() == rhs.GetData();
    }

    std::string ToString(std::string prefix = "") const {
        std::stringstream ss{};
        ss << (int) data_;
        return ss.str();
    }

private:
    UnderlyingType data_;
};


template<typename UnderlyingType, std::size_t BitSize>
class Signed {
public:
    Signed(): data_{0}{}
    Signed(UnderlyingType value): data_{value} {}

    static Signed FromJson(json j) {
        return Signed(j.get<UnderlyingType>());
    }

    static Signed Decode(Buffer& buffer, Endianess endianess=Endianess::Little) {
        auto word = buffer.GetWord(BitSize, true, endianess);
        return Signed(static_cast<UnderlyingType>(word));
    }

    json DecodeJson() const {
        return GetData();
    }

    void Encode(Buffer& buffer, Endianess endianess=Endianess::Little) const {
        buffer.PushWord<UnderlyingType, BitSize>(data_, endianess) ;
    }

    UnderlyingType GetData() const {
        return data_;
    }

    inline bool operator==(const Signed& rhs) const
    {
        return GetData() == rhs.GetData();
    }

    std::string ToString(std::string prefix = "") const {
        std::stringstream ss{};
        ss << (int) data_;
        return ss.str();
    }

private:
    UnderlyingType data_;
};

class Float {
public:
    using UnderlyingType = float;
    static constexpr unsigned BitSize = 32;

    Float(): data_{0.0}{}
    Float(UnderlyingType value): data_{value} {}

    static Float FromJson(json j) {
        return Float(j.get<UnderlyingType>());
    }

    static Float Decode(Buffer& buffer, Endianess endianess=Endianess::Little) {
        auto word = buffer.GetWord(BitSize, false, endianess);

        UnderlyingType data{};
        std::memcpy(&data, &word, 4);

        return Float(data);
    }

    json DecodeJson() const {
        return GetData();
    }

    void Encode(Buffer& buffer, Endianess endianess = Endianess::Little) const {
        std::uint32_t tmp = 0;
        std::memcpy(&tmp, &data_, 4);
        buffer.PushWord<std::uint32_t, BitSize>(tmp, endianess) ;
    }

    UnderlyingType GetData() const {
        return data_;
    }

    inline bool operator==(const Float& rhs) const
    {
        return std::fabs(GetData() - rhs.GetData()) <= std::numeric_limits<float>::epsilon();
    }

    std::string ToString(std::string prefix = "") const {
        std::stringstream ss{};
        ss << data_;
        return ss.str();
    }

private:
    UnderlyingType data_;
};


class Double {
public:
    using UnderlyingType = double;
    static constexpr unsigned BitSize = 64;

    Double(): data_{0.0}{}
    Double(UnderlyingType value): data_{value} {}
    static Double FromJson(json j) {
        return Double(j.get<UnderlyingType>());
    }

    static Double Decode(Buffer& buffer, Endianess endianess=Endianess::Little) {
        auto word = buffer.GetWord(BitSize, false, endianess);

        UnderlyingType data{};
        std::memcpy(&data, &word, 8);

        return Double(data);
    }

    json DecodeJson() const {
        return GetData();
    }

    void Encode(Buffer& buffer, Endianess endianess=Endianess::Little) const {
        std::uint64_t tmp = 0;
        std::memcpy(&tmp, &data_, 8);
        buffer.PushWord<std::uint64_t, BitSize>(tmp, endianess) ;
    }

    UnderlyingType GetData() const {
        return data_;
    }

    inline bool operator==(const Double& rhs) const
    {
        return std::fabs(GetData() - rhs.GetData()) <= std::numeric_limits<double>::epsilon();
    }


    std::string ToString(std::string prefix = "") const {
        std::stringstream ss{};
        ss << data_;
        return ss.str();
    }

private:
    UnderlyingType data_;
};

template<typename T, std::size_t N>
class Array {
    public:

    Array(): data_{} {}
    Array(std::array<T, N> value): data_{value} {}
    Array(std::initializer_list<T> ls) {
        std::copy(ls.begin(), ls.end(), data_.begin());
    }

    static Array FromJson(json j) {
        std::array<T, N> data{0};

        for (std::size_t i=0; i<N && i<j.size(); i++) {
            data[i] = T::FromJson(j[i]);
        }

        return Array(data);
    }

    static Array Decode(Buffer& buffer, Endianess endianess = Endianess::Little) {
        std::array<T, N> data{0};

        for (std::size_t i=0; i<N; i++) {
            data[i] = T::Decode(buffer, endianess);
        }

        return Array(data);
    }

    json DecodeJson() const {
        json j{};

        for (const auto& x: GetData()) {
            j.push_back(x.DecodeJson());
        }

        return j;
    }

    void Encode(Buffer& buffer, Endianess endianess=Endianess::Little) const {
        for (std::size_t i=0; i<N; i++) {
            data_[i].Encode(buffer, endianess);
        }
    }

    const std::array<T,N>& GetData() const {
        return data_;
    }

    inline bool operator==(const Array& rhs) const
    {
        return GetData() == rhs.GetData();
    }

    std::string ToString(std::string prefix="") const {
        std::stringstream ss{};
        ss << "[";
        for (std::size_t i=0; i<N-1; i++){
            ss << data_[i].ToString() << ", ";
        }
        ss << data_[N-1].ToString() << "]";
        return ss.str();
    }

private:
    std::array<T, N> data_;
};


class String {
    public:

    String(): data_{} {}
    String(const std::string& value): data_{value} {}
    String(const char* value): data_{value} {}

    static String FromJson(json j) {
        return String(j.get<std::string>());
    }

    static String Decode(Buffer& buffer, Endianess endianess=Endianess::Little) {
        std::string data{};
        auto len = Unsigned<std::uint32_t, 32>::Decode(buffer).GetData();
        for (unsigned i=0; i<len; i++) {
            data.push_back(Unsigned<std::uint8_t, 8>::Decode(buffer, endianess).GetData());
        }

        return String(data);
    }

    json DecodeJson() const {
        return GetData();
    }

    void Encode(Buffer& buffer, Endianess endianess=Endianess::Little) const {
        Unsigned<std::uint32_t, 32>(data_.size()).Encode(buffer);
        for (const auto& c: data_) {
            Unsigned<std::uint8_t, 8>(c).Encode(buffer, endianess);
        }
    }

    std::string GetData() const {
        return data_;
    }

    inline bool operator==(const String& rhs) const
    {
        return GetData() == rhs.GetData();
    }

    std::string ToString(std::string prefix="") const {
        return data_;
    }


private:
    std::string data_;
};

template<typename T>
class DynamicArray {
    public:

    DynamicArray(): data_{} {}
    DynamicArray(const std::vector<T>& value): data_{value} {}
    DynamicArray(const char* value): data_{value} {}
    DynamicArray(std::initializer_list<T> ls) : data_{ls} {}

    static DynamicArray FromJson(json j) {
        std::vector<T> data{};
        for (const auto& x: j) {
            data.push_back(T::FromJson(x));
        }

        return DynamicArray(data);
    }

    static DynamicArray Decode(Buffer& buffer, Endianess endianess=Endianess::Little) {
        std::vector<T> data{};
        auto len = Unsigned<std::uint32_t, 32>::Decode(buffer).GetData();
        for (unsigned i=0; i<len; i++) {
            data.push_back(T::Decode(buffer, endianess));
        }

        return DynamicArray(data);
    }

    json DecodeJson() const {
        json j{};
        for (auto x: GetData()) {
            j.push_back(x.DecodeJson());
        }
        return j;
    }

    void Encode(Buffer& buffer, Endianess endianess=Endianess::Little) const {
        Unsigned<std::uint32_t, 32>(data_.size()).Encode(buffer);
        for (auto x: data_) {
            x.Encode(buffer, endianess);
        }
    }

    std::vector<T> GetData() const {
        return data_;
    }

    inline bool operator==(const DynamicArray& rhs) const
    {
        return GetData() == rhs.GetData();
    }

    std::string ToString(std::string prefix="") const {
        std::stringstream ss{};
        ss << "[";
        for (std::size_t i=0; i<data_.size(); i++) {
            ss << data_[i].ToString();
            if (i != data_.size()-1) {
                ss << data_[i].ToString() << ", ";
            }
        }
        ss << "]";

        return ss.str();
    }


private:
    std::vector<T> data_;
};

template<typename T>
class Optional {
    public:

    Optional(const std::optional<T>& value): data_{value} {}
    Optional(): data_{std::nullopt} {}

    Optional& operator=(const T that) {
        data_ = that;
        return *this;
    }

    Optional& operator=(std::nullopt_t that) {
        data_ = that;
        return *this;
    }

    static Optional None() {
        return Optional(std::nullopt);
    }

    static Optional Some(const T& value) {
        return Optional(value);
    }

    static Optional FromJson(json j) {
        if (j.is_null()) {
            return Optional{std::nullopt};
        }
        else {
            return Optional{std::optional<T>{T::FromJson(j)}};
        }
    }

    static Optional Decode(Buffer& buffer, Endianess endianess=Endianess::Little) {
        std::optional<T> data;
        auto is_some = Unsigned<std::uint8_t, 8>::Decode(buffer).GetData();

        if (is_some) {
            data = T::Decode(buffer, endianess);
        }
        else {
            data = std::nullopt;
        }

        return Optional(data);
    }

    json DecodeJson() const {
        if (GetData().has_value()) {
            return GetData().value().DecodeJson();
        }
        else {
            return nullptr;
        }
    }

    void Encode(Buffer& buffer, Endianess endianess=Endianess::Little) const {
        Unsigned<std::uint8_t, 8>(data_.has_value() ? 1 : 0).Encode(buffer);

        if (data_.has_value()) {
            data_.value().Encode(buffer, endianess);
        }
    }

    std::optional<T> GetData() const {
        return data_;
    }

    inline bool operator==(const Optional& rhs) const
    {
        return GetData() == rhs.GetData();
    }

    std::string ToString(std::string prefix="") const {
        std::stringstream ss{};
        if (data_.has_value()) {
            ss << "Some(";
            ss << data_.value().ToString();
            ss << ")";
        }
        else {
            ss << "None";
        }

        return ss.str();
    }


private:
    std::optional<T> data_;
};
}
