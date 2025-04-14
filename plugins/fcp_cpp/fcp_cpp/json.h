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

#pragma once

#include <map>
#include <vector>
#include <string>
#include <cstdint>
#include <iostream>
#include "variant.h"

using json = rva::variant<
    std::nullptr_t,                       // json null
    bool,                                 // json boolean
    double,                               // json number
    std::int64_t,                         // json integer
    std::uint64_t,                        // json unsigned integer
    std::string,                          // json string
    std::map<std::string, rva::self_t>,   // json object, type is std::map<std::string, json_value>
    std::vector<rva::self_t>>;            // json array, type is std::vector<json_value>

void _Print(const json& j) {
    auto visitor = [](auto&& x) -> void {
        using T = std::decay_t<decltype(x)>;
        if constexpr (std::is_same_v<T, std::nullptr_t>) {
            std::cout << "null";
        }
        else if constexpr (std::is_same_v<T, bool>) {
            std::cout << (x ? "true" : "false");
        }
        else if constexpr (std::is_same_v<T, double>) {
            std::cout << x;
        }
        else if constexpr (std::is_same_v<T, std::int64_t>) {
            std::cout << x;
        }
        else if constexpr (std::is_same_v<T, std::uint64_t>) {
            std::cout << x;
        }
        else if constexpr (std::is_same_v<T, std::map<std::string, json>>) {
            std::cout << "{";
            for (const auto& [key, value] : x) {
                std::cout << key << ": ";
                _Print(value);
                std::cout << ", ";
            }
            std::cout << "}";
        }
        else if constexpr (std::is_same_v<T, std::vector<json>>) {
            std::cout << "[";
            for (const auto& value : x) {
                _Print(value);
                std::cout << ", ";
            }
            std::cout << "]";
        }
        else if constexpr (std::is_same_v<T, std::string>) {
            std::cout << "\"" << x << "\"";
        }
        else {
            std::cout << "Unimplemented";
        }
    };
    rva::visit(visitor, j);
}

void Print(const json& j) {
    _Print(j);
    std::cout << std::endl;
}
