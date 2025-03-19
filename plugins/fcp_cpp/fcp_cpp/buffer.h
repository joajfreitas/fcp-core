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

namespace fcp {

template<typename Iterator>
uint8_t get_bit(Iterator input, uint32_t bit) {
    auto byte_address = bit >> 3;
    auto intra_byte_bit_address = bit & 0b111;

    return (*(input+byte_address) >> intra_byte_bit_address) & 0b1;
}

enum class Endianess {
    Little,
    Big
};

class Buffer {
public:
    explicit Buffer(std::size_t size): buffer_((size + 7)/8), current_bit_{0} {}
    Buffer(const std::vector<uint8_t>& buffer): buffer_{buffer}, current_bit_{0} {}
    template<typename Iterator>
    Buffer(Iterator first, Iterator last): buffer_{first, last}, current_bit_{0} {}

    uint64_t GetWord(uint64_t bitlength, bool sign=false, Endianess endianess=Endianess::Little) {
        uint64_t result = 0;
        for (uint64_t i=0; i<bitlength; i++) {
            auto word = static_cast<uint64_t>(get_bit(buffer_.begin(), current_bit_ + i)) << i;
            result |= word;
        }

        uint64_t mask = 1ULL << (bitlength - 1);

        bool msb_set = (result >> (bitlength-1)) == 1;
        if (sign && msb_set && !(msb_set && bitlength == 64)) {
            result = (result ^ mask) - mask;
        }

        current_bit_ += bitlength;

        return endianess==Endianess::Little ? result : FromBigEndian(result, bitlength);
    }

    template<typename T, std::size_t Size>
    void PushWord(T word, Endianess endianess=Endianess::Little) {
        T tmp = (endianess == Endianess::Little) ? word : FromBigEndian(word, Size);
        for (std::size_t i=0; i<Size; i++) {
            SetBit((tmp >> i) & 0b1, current_bit_ + i);
        }

        current_bit_ += Size;
    }

    template<typename T>
    void PushWord(T word, std::size_t bitlength, Endianess endianess=Endianess::Little) {
        T tmp = (endianess == Endianess::Little) ? word : FromBigEndian(word, bitlength);
        for (std::size_t i=0; i<bitlength; i++) {
            SetBit((tmp >> i) & 0b1, current_bit_ + i);
        }

        current_bit_ += bitlength;
    }

    template<typename T>
    void Insert(T begin, T end) {
        buffer_.insert(buffer_.end(), begin, end);
    }

    std::vector<uint8_t> GetData() const {
        return buffer_;
    }

    std::string ToString(std::string prefix = "") const {
        std::stringstream ss{};
        ss << std::hex << "{";
        for (const auto& x: GetData()) {
            ss << (int) x << ", " ;
        }
        ss << "}";
        return ss.str();
    }

private:
    void SetBit(uint8_t bit, std::size_t bit_index) {
        auto byte_address = bit_index >> 3;
        auto intra_byte_bit_address = bit_index & 0b111;

        if (byte_address >= buffer_.size()) {
            Extend();
        }

        buffer_[byte_address] = (buffer_[byte_address] & ~((uint8_t)1 << intra_byte_bit_address)) | ((uint8_t) bit << intra_byte_bit_address);
    }

    void Extend() {
        buffer_.push_back(0);
    }

    uint64_t FromBigEndian(uint64_t value, uint64_t bitlength) {
        if (bitlength == 8) {
            return value;
        }
        else if (bitlength == 16) {
            return ((value & 0x00FF) << 8) | ((value & 0xFF00) >> 8);
        }
        else if (bitlength == 32) {
            return ((value & 0x000000FF) << 24) | ((value & 0x0000FF00) << 8) | ((value & 0x00FF0000) >> 8) | ((value & 0xFF000000) >> 24);
        }
        else if (bitlength == 64) {
            return
            ((value & 0x00000000000000FF) << 56) |
            ((value & 0x000000000000FF00) << 40) |
            ((value & 0x0000000000FF0000) << 24) |
            ((value & 0x00000000FF000000) << 8) |
            ((value & 0x000000FF00000000) >> 8) |
            ((value & 0x0000FF0000000000) >> 24) |
            ((value & 0x00FF000000000000) >> 40) |
            ((value & 0xFF00000000000000) >> 56);
        }

        throw std::runtime_error("Big endian conversion only supported for 8, 16, 32, 64 bit values");
    }

    std::vector<uint8_t> buffer_;
    std::uint32_t current_bit_;
};
}
