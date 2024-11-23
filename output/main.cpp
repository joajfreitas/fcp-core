#include "fcp.h"

#include <cstring>
#include <iostream>
#include <fstream>

using namespace std;

class StructField {
    private:
        std::string name;
        std::int32_t field_id;

class Struct {
    private:
        std::string name;
        std::map<std::string, StructField> fields;
}

class DynamicSchema {
    private:
        std::map<std::string, Struct> structs;
}

int main(char argc, char* argv[]) {
    ifstream fcp_bin(argv[1]);
    string content;

    std::stringstream buffer;
    buffer << fcp_bin.rdbuf();

    auto str = buffer.str();

    auto buf = fcp::Buffer(str.begin(), str.end());
    auto f = fcp::Fcp::Decode(buf);

    std::cout << f.to_string();

    return 0;
} 
