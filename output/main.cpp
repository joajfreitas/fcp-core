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
            std::string type
        ) : 
            name{name}, 
            size{size}, 
            type{type} 
        {}

    private:
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

    private:
        std::string name;
        std::uint32_t field_id;
        Type type;
        std::optional<std::string> unit;
        std::optional<double> min_value;
        std::optional<double> max_value;
};

class Struct {
    
public:
    Struct(std::string name, std::map<std::string, StructField> fields) : name{name}, fields{fields} {};

private:
    std::string name;
    std::map<std::string, StructField> fields;
};

class Enum {
    private:
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
                structs.insert({name, Struct(name, {})});
            }
        }

        json Decode(std::string name, std::vector<uint8_t>) {
            structs[name]

            return json{};
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

    return 0;
}
