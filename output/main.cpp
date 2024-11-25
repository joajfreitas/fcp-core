#include "fcp.h"
#include <nlohmann/json.hpp>

#include <cstring>
#include <iostream>
#include <fstream>
#include <filesystem>

using json = nlohmann::json;

class Type {
    public:
        Type(
            std::string name, 
            std::uint32_t size, 
            std::string type,
        ) : 
            name{name}, 
            size{size}, 
            type{type},
        {}

        std::string name;
        std::uint32_t size;
        std::string type;
};

class StructField {
    public:
        StructField(
                std::string name, 
                std::uint32_t field_id, 
                Type type, 
                std::optional<std::string> unit = std::nullopt, 
                std::optional<double> min_value = std::nullopt, 
                std::optional<double> max_value = std::nullopt): 
            name{name}, 
            field_id{field_id}, 
            type{type}, 
            unit{unit}, 
            min_value{min_value}, 
            max_value{max_value} {};

        std::string name;
        std::uint32_t field_id;
        Type type;
        std::optional<std::string> unit;
        std::optional<double> min_value;
        std::optional<double> max_value;
};

class Struct {
    
public:
    Struct() = default;
    Struct(std::string name, std::map<std::string, StructField> fields) : name{name}, fields{fields} {};

    std::string name;
    std::map<std::string, StructField> fields;
};

class Enum {
    public:
        Enum() = default;
        Enum(std::string name, std::map<std::string, std::int32_t> enumeration): name{name}, enumeration{enumeration} {};

        std::string name;
        std::map<std::string, std::int32_t> enumeration;
};

class SignalBlock {
    private:
    std::string name;
    std::map<std::string, std::string> fields;
};

class Impl {
    private:
        std::string name;
        std::string protocol;
        std::string type;
        std::map<std::string, std::string> fields;
        std::map<std::string, SignalBlock> signals;
};

class Rpc {
    private:
        std::string name;
        std::string input;
        std::string output;
};

class Service {
    private:
        std::string name;
        std::map<std::string, Rpc> rpcs;
};

namespace {

template<typename Iterator>
uint8_t get_bit(Iterator input, uint32_t bit) {
    auto byte_address = bit >> 3;
    auto intra_byte_bit_address = bit & 0b111;

    return (*(input+byte_address) >> intra_byte_bit_address) & 0b1;
}

class Buffer {
public:
    explicit Buffer(std::size_t size): buffer_((size + 7)/8), current_bit_{0} {}
    Buffer(const std::vector<uint8_t>& buffer): buffer_{buffer}, current_bit_{0} {}
    template<typename Iterator>
    Buffer(Iterator first, Iterator last): buffer_{first, last}, current_bit_{0} {}

    uint64_t get_word(uint64_t bitlength, bool sign=false) {
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

        return result;
    }

    template<typename T, std::size_t Size>
    void push_word(T word) {
        for (int i=0; i<Size; i++) {
            set_bit((word >> i) & 0b1, current_bit_ + i);
        }

        current_bit_ += Size;
    }

    std::vector<uint8_t> GetData() const {
        return buffer_;
    }

    std::string to_string(std::string prefix = "") const {
        std::stringstream ss{};
        ss << std::hex << "{";
        for (const auto& x: GetData()) {
            ss << (int) x << ", " ;
        }
        ss << "}";
        return ss.str();
    }

private:
    void set_bit(uint8_t bit, std::size_t bit_index) {
        auto byte_address = bit_index >> 3;
        auto intra_byte_bit_address = bit_index & 0b111;

        if (byte_address >= buffer_.size()) {
            extend();
        }

        buffer_[byte_address] = (buffer_[byte_address] & ~((uint8_t)1 << intra_byte_bit_address)) | ((uint8_t) bit << intra_byte_bit_address);
    }

    void extend() {
        buffer_.push_back(0);
    }

    std::vector<uint8_t> buffer_;
    std::uint32_t current_bit_;
};
}

class DynamicSchema {
    public:
        DynamicSchema() = default;
        
        void LoadBinarySchemaFromFile(std::filesystem::path path) {
            std::ifstream fcp_bin(path.string());
            std::stringstream buffer;
            buffer << fcp_bin.rdbuf();

            LoadBinarySchema(buffer.str());
        }

        void LoadBinarySchema(std::string schema) {
            std::cout << "load schema" << std::endl;

            auto buffer = fcp::Buffer(schema.begin(), schema.end());
            auto fcp = fcp::Fcp::Decode(buffer);
            

            for (const auto& x: fcp.GetStructs().GetData()) {
                std::string name = x.GetName().GetData();
                    
                std::map<std::string, StructField> fields{};
                for (const auto& struct_field: x.GetFields().GetData()) {
                    fields.insert({
                        struct_field.GetName().GetData(), 
                            StructField{
                                struct_field.GetName().GetData(), 
                                struct_field.GetField_id().GetData(), 
                                Type{
                                    struct_field.GetType().GetName().GetData(), 
                                    struct_field.GetType().GetSize().GetData(), 
                                    struct_field.GetType().GetType().GetData(),
                                }
                            }
                        });
                }
                structs.insert({name, Struct(name, fields)});
            }

            for (const auto& x: fcp.GetEnums().GetData()) {
                std::string name = x.GetName().GetData();
                std::map<std::string, std::int32_t> enumeration{};
                for (const auto& enum_field: x.GetEnumeration().GetData()) {
                    enumeration.insert({enum_field.GetName().GetData(), enum_field.GetValue().GetData()});
                }
                enums.insert({name, Enum{name, enumeration}});
            }
        }


        json DecodeStruct(std::string name, Buffer& buffer) {
            auto s = structs[name];
    
            auto struct_json = json{};

            for(auto [_, field]: s.fields) {
                std::cout << "decode_field" << std::endl;
                struct_json[field.name] = _Decode(field.type, buffer);
            }

            return struct_json;
        }

        
        json DecodeEnum(std::string name, Buffer& buffer) {
            auto e = enums[name];
            
            auto max_value = std::max_element(e.enumeration.begin(), e.enumeration.end(), 
                    [](const auto& a, const auto& b) {
                        return a.second < b.second;
                    })->second;

            auto bitsize = std::log2(max_value+1);

            auto enum_value = DecodeUnsigned(Type{"u" + std::to_string(bitsize), 1, "Builtin"}, buffer);

            return std::find_if(e.enumeration.begin(), e.enumeration.end(), 
                    [enum_value](const auto& x) {
                        return x.second == enum_value;
                    })->first;
        }

        json DecodeUnsigned(Type type, Buffer& buffer) {
            auto size = std::stoi(type.name.substr(1));
            return buffer.get_word(size);
        }

        json DecodeSigned(Type type, Buffer& buffer) {
            auto size = std::stoi(type.name.substr(1));
            return buffer.get_word(size, true);
        }

        json DecodeFloat32(Type type, Buffer& buffer) {
            float data;
            auto word = buffer.get_word(32);
            std::memcpy(&data, &word, sizeof(data));

            return data;
        }

        json DecodeFloat64(Type type, Buffer& buffer) {
            double data;
            auto word = buffer.get_word(64);
            std::memcpy(&data, &word, sizeof(data));

            return data;
        }

        json DecodeString(Type type, Buffer& buffer) {
            auto length = buffer.get_word(32);
            std::string data;
            for (int i=0; i<length; i++) {
                data += buffer.get_word(8);
            }
            return data;
        }

        json DecodeArray(Type type, Buffer& buffer) {
            auto length = buffer.get_word(32);
            std::vector<json> data;
            for (int i=0; i<length; i++) {
                data.push_back(_Decode(type.underlying_type, buffer));
            }

        }
    
        json _Decode(Type type, Buffer& buffer) {
            std::cout << "_Decode" << std::endl;
            if (type.type == "Builtin") {
                if (type.name[0] == 'u') {
                    return DecodeUnsigned(type, buffer);
                }
                else if (type.name[0] == 'i') {
                    return DecodeSigned(type, buffer);
                }
                else if (type.name == "f32") {
                    return DecodeFloat32(type, buffer);
                }
                else if (type.name == "f64") {
                    return DecodeFloat64(type, buffer);
                }
                else if (type.name == "str") {
                    return DecodeString(type, buffer);
                }
            }
            else if (type.type == "Struct") {
                return DecodeStruct(type.name, buffer);
            }
            else if (type.type == "Enum") {
                return DecodeEnum(type.name, buffer);
            }
            else if (type.type == "Array") {
                return DecodeArray(type, buffer);
            }
            else {
                throw std::runtime_error("Unknown type" + type.type);
            }
        }            
        json Decode(std::string name, std::vector<uint8_t> data) {
            auto buffer = Buffer{data.begin(), data.end()};
            return DecodeStruct(name, buffer);
        }


    private:
        std::map<std::string, Struct> structs;
        std::map<std::string, Enum> enums;
        std::map<std::string, Impl> impls;
        std::map<std::string, Service> services;
};

int main(int argc, char* argv[]) {

    DynamicSchema schema{};

    schema.LoadBinarySchemaFromFile(argv[1]);

    std::cout << schema.Decode("SensorReq", {1});

    return 0;
}
