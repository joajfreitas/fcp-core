#ifndef __FCP_H__
#define __FCP_H__

#include <vector>
#include <cstdint>
#include <map>
#include <any>
#include <array>
#include <variant>
#include <memory>
#include <string>
#include <iostream>
#include <sstream>

namespace fcp {

namespace {

template<typename Iterator>
uint8_t get_bit(Iterator input, uint8_t bit) {
    auto byte_address = bit >> 3;
    auto intra_byte_bit_address = bit & 0b111;

    return (*(input+byte_address) >> intra_byte_bit_address) & 0b1;
}

class Buffer {
public:
    Buffer(std::size_t size): buffer_((size + 7)/8) {}
    Buffer(const std::vector<uint8_t>& buffer): buffer_{buffer} {}
    template<typename Iterator>
    Buffer(Iterator first, Iterator last): buffer_{first, last} {}


    uint64_t get_word(std::size_t bitstart, std::size_t bitlength) {
        uint64_t result = 0;
        for (int i=0; i<bitlength; i++) {
            result |= get_bit(buffer_.begin(), bitstart + i) << i;
        }

        return result;
    }

    template<typename T, std::size_t Size>
    void push_word(T word, std::size_t bitstart) {
        for (int i=0; i<Size; i++) {
            set_bit((word >> i) & 0b1, bitstart + i);
        }
    }

    std::vector<uint8_t> GetData() {
        return buffer_;
    }

private:
    void set_bit(uint8_t bit, std::size_t bit_index) {
        auto byte_address = bit_index >> 3;
        auto intra_byte_bit_address = bit_index & 0b111;

        buffer_[byte_address] = (buffer_[byte_address] & ~((uint8_t)1 << intra_byte_bit_address)) | ((uint8_t) bit << intra_byte_bit_address);

    }

private:
    std::vector<uint8_t> buffer_;
};
}

template<std::size_t Size>
class Uint8 {
public:
    Uint8(){}
    Uint8(std::uint8_t value): data_{value} {}

    Uint8(Buffer& buffer, std::size_t bitstart) {
        auto word = buffer.get_word(bitstart, Size);
        data_ = static_cast<std::uint8_t>(word);
    }

    void _encode(Buffer& buffer, std::size_t bitstart) {
        buffer.push_word<uint8_t, Size>(data_, bitstart) ;
    }

    static std::size_t GetSize() {
        return Size;
    }

    inline bool operator==(const Uint8& rhs) const
    {
        return true;
    }

    uint8_t GetData() const {
        return data_;
    }

    std::string to_string(std::string prefix = "") const {
        std::stringstream ss{};
        ss << (int) data_;
        return ss.str();
    }

private:
    std::uint8_t data_;
};


template<typename UnderlyingType>
class State {
public:
    static constexpr UnderlyingType S1 = 0;
    static constexpr UnderlyingType S2 = 1;
    static constexpr UnderlyingType S3 = 2;

    State(): data_{} {}
    State(UnderlyingType value): data_{value} {}

    State(Buffer& buffer, std::size_t bitstart=0) {
        data_ = buffer.get_word(bitstart, GetSize());
    }

    void _encode(Buffer& buffer, std::size_t bitstart) {
        buffer.push_word<UnderlyingType, GetSize()>(data_, bitstart) ;
    }

    static constexpr std::size_t GetSize() {
        return 2;
    }

    UnderlyingType GetData() const {
        return data_;
    }

    inline bool operator==(const State& rhs) const
    {
        return GetData() == rhs.GetData();
    }

    std::string to_string(std::string prefix="") const {
        std::stringstream ss{};

        switch(GetData()) {
            case State::S1:
                return "S1";
            case State::S2:
                return "S2";
            case State::S3:
                return "S3";
            default:
                return "DecodingError";
        }
    }


private:
    UnderlyingType data_;
};

template<typename T, std::size_t N>
class Array {
    public:

    Array(): data_{} {}
    Array(std::array<T, N> value): data_{value} {}

    Array(Buffer& buffer, std::size_t bitstart=0) {
        for (int i=0; i<N; i++) {
            data_[i] = T(buffer, bitstart);
            bitstart += T::GetSize();
        }
    }

    void _encode(Buffer& buffer, std::size_t bitstart) {
        for (int i=0; i<N; i++) {
            data_[i]._encode(buffer, bitstart + i*T::GetSize());
        }
    }

    static std::size_t GetSize() {
        return N*T::GetSize();
    }

    const std::array<T,N>& GetData() const {
        return data_;
    }

    inline bool operator==(const Array& rhs) const
    {
        return GetData() == rhs.GetData();
    }

    std::string to_string(std::string prefix="") const {
        std::stringstream ss{};
        ss << "[";
        for (int i=0; i<N-1; i++){
            ss << data_[i].to_string() << ", ";
        }
        ss << data_[N-1].to_string() << "]";
        return ss.str();
    }


private:
    std::array<T, N> data_;
};

struct Foo {
    using S1Type = Array<Array<Uint8<8>, 4>, 4>;
    using S2Type = Uint8<8>;
    using S3Type = State<uint8_t>;

    Foo(): s1_{}, s2_{} , s3_{} {}
    Foo(S1Type s1, S2Type s2, S3Type s3): s1_{s1}, s2_{s2} , s3_{s3} {}

    Foo(Buffer& buffer, std::size_t bitstart = 0) {
        s1_ = S1Type(buffer, bitstart);
        bitstart += S1Type::GetSize();
        s2_ = S2Type(buffer, bitstart);
        bitstart += S2Type::GetSize();
        s3_ = S3Type(buffer, bitstart);
        bitstart += S3Type::GetSize();
    }

    void _encode(Buffer& buffer, std::size_t bitstart) {
        s1_._encode(buffer, bitstart);
        bitstart += S1Type::GetSize();
        s2_._encode(buffer, bitstart);
        bitstart += S2Type::GetSize();
        s3_._encode(buffer, bitstart);
        bitstart += S3Type::GetSize();
    }

    Buffer encode() {
        Buffer buffer{GetSize()};
        _encode(buffer, 0);
        return buffer;
    }

    S1Type GetS1() const {
        return s1_;
    }

    S2Type GetS2() const {
        return s2_;
    }

    S3Type GetS3() const {
        return s3_;
    }

    static std::size_t GetSize() {
        return S1Type::GetSize() + S2Type::GetSize() + S3Type::GetSize();
    }

    inline bool operator==(const Foo& rhs) const
    {
        return s1_ == rhs.GetS1() && s2_ == rhs.GetS2() && s3_ == rhs.GetS3();
    }

    std::string to_string(std::string prefix="") const {
        std::stringstream ss{};
        auto p = prefix + "\t";
        ss << "Foo {" << std::endl;
        ss << p << "s1: " << s1_.to_string(p) << std::endl;
        ss << p << "s2: " << s2_.to_string(p) << std::endl;
        ss << p << "s3: " << s3_.to_string(p) << std::endl;
        ss << prefix << "}" << std::endl;
        return ss.str();
    }

private:
    S1Type s1_;
    S2Type s2_;
    S3Type s3_;

};


struct Bar {
    using S1Type = Foo;
    using S2Type = Array<Array<Uint8<8>, 2>, 2>;

    Bar(S1Type s1, S2Type s2): s1_{s1}, s2_{s2} {}

    Bar(Buffer& buffer, std::size_t bitstart = 0) {
        s1_ = S1Type(buffer, bitstart);
        bitstart += S1Type::GetSize();
        s2_ = S2Type(buffer, bitstart);
        bitstart += S2Type::GetSize();
    }

    void _encode(Buffer& buffer, std::size_t bitstart) {
        s1_._encode(buffer, bitstart);
        bitstart += S1Type::GetSize();
        s2_._encode(buffer, bitstart);
        bitstart += S2Type::GetSize();
    }

    Buffer encode() {
        Buffer buffer{GetSize()};
        _encode(buffer, 0);
        return buffer;
    }

    S1Type GetS1() const {
        return s1_;
    }

    S2Type GetS2() const {
        return s2_;
    }

    static std::size_t GetSize() {
        return S1Type::GetSize() + S2Type::GetSize();
    }

    inline bool operator==(const Bar& rhs) const
    {
        return s1_ == rhs.GetS1() && s2_ == rhs.GetS2();
    }

    std::string to_string(std::string prefix = "") const {
        std::stringstream ss{};
        auto p = prefix + "\t";
        ss << "Bar {" << std::endl;
        ss << p << "s1: " << s1_.to_string(p) << std::endl;
        ss << p << "s2: " << s2_.to_string(p) << std::endl;
        ss << prefix << "}" << std::endl;
        return ss.str();
    }

private:
    S1Type s1_;
    S2Type s2_;
};


} // namespace fcp

#endif // __FCP_CAN_H__
