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

namespace reflection {


using json = nlohmann::json;



struct MetaData {
    using LineType = Signed<std::int32_t, 32>;
    using EndLineType = Signed<std::int32_t, 32>;
    using ColumnType = Signed<std::int32_t, 32>;
    using EndColumnType = Signed<std::int32_t, 32>;
    using StartPosType = Signed<std::int32_t, 32>;
    using EndPosType = Signed<std::int32_t, 32>;
    using FilenameType = String;

    MetaData():
        line_{},
        end_line_{},
        column_{},
        end_column_{},
        start_pos_{},
        end_pos_{},
        filename_{}
    {}

    MetaData(LineType line,EndLineType end_line,ColumnType column,EndColumnType end_column,StartPosType start_pos,EndPosType end_pos,FilenameType filename):
        line_{line},
        end_line_{end_line},
        column_{column},
        end_column_{end_column},
        start_pos_{start_pos},
        end_pos_{end_pos},
        filename_{filename}
    {}

    static MetaData FromJson(json j){
        return MetaData {
            LineType::FromJson(j["line"]),
            EndLineType::FromJson(j["end_line"]),
            ColumnType::FromJson(j["column"]),
            EndColumnType::FromJson(j["end_column"]),
            StartPosType::FromJson(j["start_pos"]),
            EndPosType::FromJson(j["end_pos"]),
            FilenameType::FromJson(j["filename"]),
        };
    }

    static MetaData Decode(Buffer& buffer, Endianess endianess=Endianess::Little) {
        auto line = LineType::Decode(buffer, endianess);
        auto end_line = EndLineType::Decode(buffer, endianess);
        auto column = ColumnType::Decode(buffer, endianess);
        auto end_column = EndColumnType::Decode(buffer, endianess);
        auto start_pos = StartPosType::Decode(buffer, endianess);
        auto end_pos = EndPosType::Decode(buffer, endianess);
        auto filename = FilenameType::Decode(buffer, endianess);

        return MetaData(line,end_line,column,end_column,start_pos,end_pos,filename);
    }

    template<typename Iterator>
    static MetaData Decode(Iterator begin, Iterator end) {
        auto buffer = Buffer{begin, end};
        return MetaData::Decode(buffer);
    }

    json DecodeJson() const {
        json j{};
        j["line"] = line_.DecodeJson();
        j["end_line"] = end_line_.DecodeJson();
        j["column"] = column_.DecodeJson();
        j["end_column"] = end_column_.DecodeJson();
        j["start_pos"] = start_pos_.DecodeJson();
        j["end_pos"] = end_pos_.DecodeJson();
        j["filename"] = filename_.DecodeJson();
        return j;
    }

    Buffer Encode(Endianess endianess=Endianess::Little) {
        Buffer buffer{0};
        Encode(buffer, endianess);
        return buffer;
    }

    void Encode(Buffer& buffer, Endianess endianess=Endianess::Little) const {
        line_.Encode(buffer, endianess);
        end_line_.Encode(buffer, endianess);
        column_.Encode(buffer, endianess);
        end_column_.Encode(buffer, endianess);
        start_pos_.Encode(buffer, endianess);
        end_pos_.Encode(buffer, endianess);
        filename_.Encode(buffer, endianess);
    }
    LineType GetLine() const {
        return line_;
    }
    EndLineType GetEndLine() const {
        return end_line_;
    }
    ColumnType GetColumn() const {
        return column_;
    }
    EndColumnType GetEndColumn() const {
        return end_column_;
    }
    StartPosType GetStartPos() const {
        return start_pos_;
    }
    EndPosType GetEndPos() const {
        return end_pos_;
    }
    FilenameType GetFilename() const {
        return filename_;
    }
    LineType& ViewLine() {
        return line_;
    }
    EndLineType& ViewEndLine() {
        return end_line_;
    }
    ColumnType& ViewColumn() {
        return column_;
    }
    EndColumnType& ViewEndColumn() {
        return end_column_;
    }
    StartPosType& ViewStartPos() {
        return start_pos_;
    }
    EndPosType& ViewEndPos() {
        return end_pos_;
    }
    FilenameType& ViewFilename() {
        return filename_;
    }
    inline bool operator==(const MetaData& rhs) const {
        return  line_ == rhs.GetLine()
        	&& end_line_ == rhs.GetEndLine()
        	&& column_ == rhs.GetColumn()
        	&& end_column_ == rhs.GetEndColumn()
        	&& start_pos_ == rhs.GetStartPos()
        	&& end_pos_ == rhs.GetEndPos()
        	&& filename_ == rhs.GetFilename();
    }

    std::string ToString(std::string prefix = "") const {
        std::stringstream ss{};
        auto p = prefix + "\t";
        ss << "MetaData {" << std::endl;
        ss << p << "line: " << line_.ToString(p) << std::endl;
        ss << p << "end_line: " << end_line_.ToString(p) << std::endl;
        ss << p << "column: " << column_.ToString(p) << std::endl;
        ss << p << "end_column: " << end_column_.ToString(p) << std::endl;
        ss << p << "start_pos: " << start_pos_.ToString(p) << std::endl;
        ss << p << "end_pos: " << end_pos_.ToString(p) << std::endl;
        ss << p << "filename: " << filename_.ToString(p) << std::endl;
        ss << prefix << "}" << std::endl;
        return ss.str();
    }

private:
    LineType line_;
    EndLineType end_line_;
    ColumnType column_;
    EndColumnType end_column_;
    StartPosType start_pos_;
    EndPosType end_pos_;
    FilenameType filename_;
};


struct Type {
    using NameType = String;
    using SizeType = Unsigned<std::uint32_t, 32>;
    using TypeType = String;

    Type():
        name_{},
        size_{},
        type_{}
    {}

    Type(NameType name,SizeType size,TypeType type):
        name_{name},
        size_{size},
        type_{type}
    {}

    static Type FromJson(json j){
        return Type {
            NameType::FromJson(j["name"]),
            SizeType::FromJson(j["size"]),
            TypeType::FromJson(j["type"]),
        };
    }

    static Type Decode(Buffer& buffer, Endianess endianess=Endianess::Little) {
        auto name = NameType::Decode(buffer, endianess);
        auto size = SizeType::Decode(buffer, endianess);
        auto type = TypeType::Decode(buffer, endianess);

        return Type(name,size,type);
    }

    template<typename Iterator>
    static Type Decode(Iterator begin, Iterator end) {
        auto buffer = Buffer{begin, end};
        return Type::Decode(buffer);
    }

    json DecodeJson() const {
        json j{};
        j["name"] = name_.DecodeJson();
        j["size"] = size_.DecodeJson();
        j["type"] = type_.DecodeJson();
        return j;
    }

    Buffer Encode(Endianess endianess=Endianess::Little) {
        Buffer buffer{0};
        Encode(buffer, endianess);
        return buffer;
    }

    void Encode(Buffer& buffer, Endianess endianess=Endianess::Little) const {
        name_.Encode(buffer, endianess);
        size_.Encode(buffer, endianess);
        type_.Encode(buffer, endianess);
    }
    NameType GetName() const {
        return name_;
    }
    SizeType GetSize() const {
        return size_;
    }
    TypeType GetType() const {
        return type_;
    }
    NameType& ViewName() {
        return name_;
    }
    SizeType& ViewSize() {
        return size_;
    }
    TypeType& ViewType() {
        return type_;
    }
    inline bool operator==(const Type& rhs) const {
        return  name_ == rhs.GetName()
        	&& size_ == rhs.GetSize()
        	&& type_ == rhs.GetType();
    }

    std::string ToString(std::string prefix = "") const {
        std::stringstream ss{};
        auto p = prefix + "\t";
        ss << "Type {" << std::endl;
        ss << p << "name: " << name_.ToString(p) << std::endl;
        ss << p << "size: " << size_.ToString(p) << std::endl;
        ss << p << "type: " << type_.ToString(p) << std::endl;
        ss << prefix << "}" << std::endl;
        return ss.str();
    }

private:
    NameType name_;
    SizeType size_;
    TypeType type_;
};


struct StructField {
    using NameType = String;
    using FieldIdType = Unsigned<std::uint32_t, 32>;
    using TypeType = DynamicArray<Type>;
    using UnitType = Optional<String>;
    using MinValueType = Optional<Double>;
    using MaxValueType = Optional<Double>;
    using MetaType = Optional<MetaData>;

    StructField():
        name_{},
        field_id_{},
        type_{},
        unit_{},
        min_value_{},
        max_value_{},
        meta_{}
    {}

    StructField(NameType name,FieldIdType field_id,TypeType type,UnitType unit,MinValueType min_value,MaxValueType max_value,MetaType meta):
        name_{name},
        field_id_{field_id},
        type_{type},
        unit_{unit},
        min_value_{min_value},
        max_value_{max_value},
        meta_{meta}
    {}

    static StructField FromJson(json j){
        return StructField {
            NameType::FromJson(j["name"]),
            FieldIdType::FromJson(j["field_id"]),
            TypeType::FromJson(j["type"]),
            UnitType::FromJson(j["unit"]),
            MinValueType::FromJson(j["min_value"]),
            MaxValueType::FromJson(j["max_value"]),
            MetaType::FromJson(j["meta"]),
        };
    }

    static StructField Decode(Buffer& buffer, Endianess endianess=Endianess::Little) {
        auto name = NameType::Decode(buffer, endianess);
        auto field_id = FieldIdType::Decode(buffer, endianess);
        auto type = TypeType::Decode(buffer, endianess);
        auto unit = UnitType::Decode(buffer, endianess);
        auto min_value = MinValueType::Decode(buffer, endianess);
        auto max_value = MaxValueType::Decode(buffer, endianess);
        auto meta = MetaType::Decode(buffer, endianess);

        return StructField(name,field_id,type,unit,min_value,max_value,meta);
    }

    template<typename Iterator>
    static StructField Decode(Iterator begin, Iterator end) {
        auto buffer = Buffer{begin, end};
        return StructField::Decode(buffer);
    }

    json DecodeJson() const {
        json j{};
        j["name"] = name_.DecodeJson();
        j["field_id"] = field_id_.DecodeJson();
        j["type"] = type_.DecodeJson();
        j["unit"] = unit_.DecodeJson();
        j["min_value"] = min_value_.DecodeJson();
        j["max_value"] = max_value_.DecodeJson();
        j["meta"] = meta_.DecodeJson();
        return j;
    }

    Buffer Encode(Endianess endianess=Endianess::Little) {
        Buffer buffer{0};
        Encode(buffer, endianess);
        return buffer;
    }

    void Encode(Buffer& buffer, Endianess endianess=Endianess::Little) const {
        name_.Encode(buffer, endianess);
        field_id_.Encode(buffer, endianess);
        type_.Encode(buffer, endianess);
        unit_.Encode(buffer, endianess);
        min_value_.Encode(buffer, endianess);
        max_value_.Encode(buffer, endianess);
        meta_.Encode(buffer, endianess);
    }
    NameType GetName() const {
        return name_;
    }
    FieldIdType GetFieldId() const {
        return field_id_;
    }
    TypeType GetType() const {
        return type_;
    }
    UnitType GetUnit() const {
        return unit_;
    }
    MinValueType GetMinValue() const {
        return min_value_;
    }
    MaxValueType GetMaxValue() const {
        return max_value_;
    }
    MetaType GetMeta() const {
        return meta_;
    }
    NameType& ViewName() {
        return name_;
    }
    FieldIdType& ViewFieldId() {
        return field_id_;
    }
    TypeType& ViewType() {
        return type_;
    }
    UnitType& ViewUnit() {
        return unit_;
    }
    MinValueType& ViewMinValue() {
        return min_value_;
    }
    MaxValueType& ViewMaxValue() {
        return max_value_;
    }
    MetaType& ViewMeta() {
        return meta_;
    }
    inline bool operator==(const StructField& rhs) const {
        return  name_ == rhs.GetName()
        	&& field_id_ == rhs.GetFieldId()
        	&& type_ == rhs.GetType()
        	&& unit_ == rhs.GetUnit()
        	&& min_value_ == rhs.GetMinValue()
        	&& max_value_ == rhs.GetMaxValue()
        	&& meta_ == rhs.GetMeta();
    }

    std::string ToString(std::string prefix = "") const {
        std::stringstream ss{};
        auto p = prefix + "\t";
        ss << "StructField {" << std::endl;
        ss << p << "name: " << name_.ToString(p) << std::endl;
        ss << p << "field_id: " << field_id_.ToString(p) << std::endl;
        ss << p << "type: " << type_.ToString(p) << std::endl;
        ss << p << "unit: " << unit_.ToString(p) << std::endl;
        ss << p << "min_value: " << min_value_.ToString(p) << std::endl;
        ss << p << "max_value: " << max_value_.ToString(p) << std::endl;
        ss << p << "meta: " << meta_.ToString(p) << std::endl;
        ss << prefix << "}" << std::endl;
        return ss.str();
    }

private:
    NameType name_;
    FieldIdType field_id_;
    TypeType type_;
    UnitType unit_;
    MinValueType min_value_;
    MaxValueType max_value_;
    MetaType meta_;
};


struct Struct {
    using NameType = String;
    using FieldsType = DynamicArray<StructField>;
    using MetaType = Optional<MetaData>;

    Struct():
        name_{},
        fields_{},
        meta_{}
    {}

    Struct(NameType name,FieldsType fields,MetaType meta):
        name_{name},
        fields_{fields},
        meta_{meta}
    {}

    static Struct FromJson(json j){
        return Struct {
            NameType::FromJson(j["name"]),
            FieldsType::FromJson(j["fields"]),
            MetaType::FromJson(j["meta"]),
        };
    }

    static Struct Decode(Buffer& buffer, Endianess endianess=Endianess::Little) {
        auto name = NameType::Decode(buffer, endianess);
        auto fields = FieldsType::Decode(buffer, endianess);
        auto meta = MetaType::Decode(buffer, endianess);

        return Struct(name,fields,meta);
    }

    template<typename Iterator>
    static Struct Decode(Iterator begin, Iterator end) {
        auto buffer = Buffer{begin, end};
        return Struct::Decode(buffer);
    }

    json DecodeJson() const {
        json j{};
        j["name"] = name_.DecodeJson();
        j["fields"] = fields_.DecodeJson();
        j["meta"] = meta_.DecodeJson();
        return j;
    }

    Buffer Encode(Endianess endianess=Endianess::Little) {
        Buffer buffer{0};
        Encode(buffer, endianess);
        return buffer;
    }

    void Encode(Buffer& buffer, Endianess endianess=Endianess::Little) const {
        name_.Encode(buffer, endianess);
        fields_.Encode(buffer, endianess);
        meta_.Encode(buffer, endianess);
    }
    NameType GetName() const {
        return name_;
    }
    FieldsType GetFields() const {
        return fields_;
    }
    MetaType GetMeta() const {
        return meta_;
    }
    NameType& ViewName() {
        return name_;
    }
    FieldsType& ViewFields() {
        return fields_;
    }
    MetaType& ViewMeta() {
        return meta_;
    }
    inline bool operator==(const Struct& rhs) const {
        return  name_ == rhs.GetName()
        	&& fields_ == rhs.GetFields()
        	&& meta_ == rhs.GetMeta();
    }

    std::string ToString(std::string prefix = "") const {
        std::stringstream ss{};
        auto p = prefix + "\t";
        ss << "Struct {" << std::endl;
        ss << p << "name: " << name_.ToString(p) << std::endl;
        ss << p << "fields: " << fields_.ToString(p) << std::endl;
        ss << p << "meta: " << meta_.ToString(p) << std::endl;
        ss << prefix << "}" << std::endl;
        return ss.str();
    }

private:
    NameType name_;
    FieldsType fields_;
    MetaType meta_;
};


struct Enumeration {
    using NameType = String;
    using ValueType = Signed<std::int32_t, 32>;
    using MetaType = Optional<MetaData>;

    Enumeration():
        name_{},
        value_{},
        meta_{}
    {}

    Enumeration(NameType name,ValueType value,MetaType meta):
        name_{name},
        value_{value},
        meta_{meta}
    {}

    static Enumeration FromJson(json j){
        return Enumeration {
            NameType::FromJson(j["name"]),
            ValueType::FromJson(j["value"]),
            MetaType::FromJson(j["meta"]),
        };
    }

    static Enumeration Decode(Buffer& buffer, Endianess endianess=Endianess::Little) {
        auto name = NameType::Decode(buffer, endianess);
        auto value = ValueType::Decode(buffer, endianess);
        auto meta = MetaType::Decode(buffer, endianess);

        return Enumeration(name,value,meta);
    }

    template<typename Iterator>
    static Enumeration Decode(Iterator begin, Iterator end) {
        auto buffer = Buffer{begin, end};
        return Enumeration::Decode(buffer);
    }

    json DecodeJson() const {
        json j{};
        j["name"] = name_.DecodeJson();
        j["value"] = value_.DecodeJson();
        j["meta"] = meta_.DecodeJson();
        return j;
    }

    Buffer Encode(Endianess endianess=Endianess::Little) {
        Buffer buffer{0};
        Encode(buffer, endianess);
        return buffer;
    }

    void Encode(Buffer& buffer, Endianess endianess=Endianess::Little) const {
        name_.Encode(buffer, endianess);
        value_.Encode(buffer, endianess);
        meta_.Encode(buffer, endianess);
    }
    NameType GetName() const {
        return name_;
    }
    ValueType GetValue() const {
        return value_;
    }
    MetaType GetMeta() const {
        return meta_;
    }
    NameType& ViewName() {
        return name_;
    }
    ValueType& ViewValue() {
        return value_;
    }
    MetaType& ViewMeta() {
        return meta_;
    }
    inline bool operator==(const Enumeration& rhs) const {
        return  name_ == rhs.GetName()
        	&& value_ == rhs.GetValue()
        	&& meta_ == rhs.GetMeta();
    }

    std::string ToString(std::string prefix = "") const {
        std::stringstream ss{};
        auto p = prefix + "\t";
        ss << "Enumeration {" << std::endl;
        ss << p << "name: " << name_.ToString(p) << std::endl;
        ss << p << "value: " << value_.ToString(p) << std::endl;
        ss << p << "meta: " << meta_.ToString(p) << std::endl;
        ss << prefix << "}" << std::endl;
        return ss.str();
    }

private:
    NameType name_;
    ValueType value_;
    MetaType meta_;
};


struct Enum {
    using NameType = String;
    using EnumerationType = DynamicArray<Enumeration>;
    using MetaType = Optional<MetaData>;

    Enum():
        name_{},
        enumeration_{},
        meta_{}
    {}

    Enum(NameType name,EnumerationType enumeration,MetaType meta):
        name_{name},
        enumeration_{enumeration},
        meta_{meta}
    {}

    static Enum FromJson(json j){
        return Enum {
            NameType::FromJson(j["name"]),
            EnumerationType::FromJson(j["enumeration"]),
            MetaType::FromJson(j["meta"]),
        };
    }

    static Enum Decode(Buffer& buffer, Endianess endianess=Endianess::Little) {
        auto name = NameType::Decode(buffer, endianess);
        auto enumeration = EnumerationType::Decode(buffer, endianess);
        auto meta = MetaType::Decode(buffer, endianess);

        return Enum(name,enumeration,meta);
    }

    template<typename Iterator>
    static Enum Decode(Iterator begin, Iterator end) {
        auto buffer = Buffer{begin, end};
        return Enum::Decode(buffer);
    }

    json DecodeJson() const {
        json j{};
        j["name"] = name_.DecodeJson();
        j["enumeration"] = enumeration_.DecodeJson();
        j["meta"] = meta_.DecodeJson();
        return j;
    }

    Buffer Encode(Endianess endianess=Endianess::Little) {
        Buffer buffer{0};
        Encode(buffer, endianess);
        return buffer;
    }

    void Encode(Buffer& buffer, Endianess endianess=Endianess::Little) const {
        name_.Encode(buffer, endianess);
        enumeration_.Encode(buffer, endianess);
        meta_.Encode(buffer, endianess);
    }
    NameType GetName() const {
        return name_;
    }
    EnumerationType GetEnumeration() const {
        return enumeration_;
    }
    MetaType GetMeta() const {
        return meta_;
    }
    NameType& ViewName() {
        return name_;
    }
    EnumerationType& ViewEnumeration() {
        return enumeration_;
    }
    MetaType& ViewMeta() {
        return meta_;
    }
    inline bool operator==(const Enum& rhs) const {
        return  name_ == rhs.GetName()
        	&& enumeration_ == rhs.GetEnumeration()
        	&& meta_ == rhs.GetMeta();
    }

    std::string ToString(std::string prefix = "") const {
        std::stringstream ss{};
        auto p = prefix + "\t";
        ss << "Enum {" << std::endl;
        ss << p << "name: " << name_.ToString(p) << std::endl;
        ss << p << "enumeration: " << enumeration_.ToString(p) << std::endl;
        ss << p << "meta: " << meta_.ToString(p) << std::endl;
        ss << prefix << "}" << std::endl;
        return ss.str();
    }

private:
    NameType name_;
    EnumerationType enumeration_;
    MetaType meta_;
};


struct DictField {
    using NameType = String;
    using ValueType = String;

    DictField():
        name_{},
        value_{}
    {}

    DictField(NameType name,ValueType value):
        name_{name},
        value_{value}
    {}

    static DictField FromJson(json j){
        return DictField {
            NameType::FromJson(j["name"]),
            ValueType::FromJson(j["value"]),
        };
    }

    static DictField Decode(Buffer& buffer, Endianess endianess=Endianess::Little) {
        auto name = NameType::Decode(buffer, endianess);
        auto value = ValueType::Decode(buffer, endianess);

        return DictField(name,value);
    }

    template<typename Iterator>
    static DictField Decode(Iterator begin, Iterator end) {
        auto buffer = Buffer{begin, end};
        return DictField::Decode(buffer);
    }

    json DecodeJson() const {
        json j{};
        j["name"] = name_.DecodeJson();
        j["value"] = value_.DecodeJson();
        return j;
    }

    Buffer Encode(Endianess endianess=Endianess::Little) {
        Buffer buffer{0};
        Encode(buffer, endianess);
        return buffer;
    }

    void Encode(Buffer& buffer, Endianess endianess=Endianess::Little) const {
        name_.Encode(buffer, endianess);
        value_.Encode(buffer, endianess);
    }
    NameType GetName() const {
        return name_;
    }
    ValueType GetValue() const {
        return value_;
    }
    NameType& ViewName() {
        return name_;
    }
    ValueType& ViewValue() {
        return value_;
    }
    inline bool operator==(const DictField& rhs) const {
        return  name_ == rhs.GetName()
        	&& value_ == rhs.GetValue();
    }

    std::string ToString(std::string prefix = "") const {
        std::stringstream ss{};
        auto p = prefix + "\t";
        ss << "DictField {" << std::endl;
        ss << p << "name: " << name_.ToString(p) << std::endl;
        ss << p << "value: " << value_.ToString(p) << std::endl;
        ss << prefix << "}" << std::endl;
        return ss.str();
    }

private:
    NameType name_;
    ValueType value_;
};


struct SignalBlock {
    using NameType = String;
    using FieldsType = DynamicArray<DictField>;
    using MetaType = Optional<MetaData>;

    SignalBlock():
        name_{},
        fields_{},
        meta_{}
    {}

    SignalBlock(NameType name,FieldsType fields,MetaType meta):
        name_{name},
        fields_{fields},
        meta_{meta}
    {}

    static SignalBlock FromJson(json j){
        return SignalBlock {
            NameType::FromJson(j["name"]),
            FieldsType::FromJson(j["fields"]),
            MetaType::FromJson(j["meta"]),
        };
    }

    static SignalBlock Decode(Buffer& buffer, Endianess endianess=Endianess::Little) {
        auto name = NameType::Decode(buffer, endianess);
        auto fields = FieldsType::Decode(buffer, endianess);
        auto meta = MetaType::Decode(buffer, endianess);

        return SignalBlock(name,fields,meta);
    }

    template<typename Iterator>
    static SignalBlock Decode(Iterator begin, Iterator end) {
        auto buffer = Buffer{begin, end};
        return SignalBlock::Decode(buffer);
    }

    json DecodeJson() const {
        json j{};
        j["name"] = name_.DecodeJson();
        j["fields"] = fields_.DecodeJson();
        j["meta"] = meta_.DecodeJson();
        return j;
    }

    Buffer Encode(Endianess endianess=Endianess::Little) {
        Buffer buffer{0};
        Encode(buffer, endianess);
        return buffer;
    }

    void Encode(Buffer& buffer, Endianess endianess=Endianess::Little) const {
        name_.Encode(buffer, endianess);
        fields_.Encode(buffer, endianess);
        meta_.Encode(buffer, endianess);
    }
    NameType GetName() const {
        return name_;
    }
    FieldsType GetFields() const {
        return fields_;
    }
    MetaType GetMeta() const {
        return meta_;
    }
    NameType& ViewName() {
        return name_;
    }
    FieldsType& ViewFields() {
        return fields_;
    }
    MetaType& ViewMeta() {
        return meta_;
    }
    inline bool operator==(const SignalBlock& rhs) const {
        return  name_ == rhs.GetName()
        	&& fields_ == rhs.GetFields()
        	&& meta_ == rhs.GetMeta();
    }

    std::string ToString(std::string prefix = "") const {
        std::stringstream ss{};
        auto p = prefix + "\t";
        ss << "SignalBlock {" << std::endl;
        ss << p << "name: " << name_.ToString(p) << std::endl;
        ss << p << "fields: " << fields_.ToString(p) << std::endl;
        ss << p << "meta: " << meta_.ToString(p) << std::endl;
        ss << prefix << "}" << std::endl;
        return ss.str();
    }

private:
    NameType name_;
    FieldsType fields_;
    MetaType meta_;
};


struct Impl {
    using NameType = String;
    using ProtocolType = String;
    using TypeType = String;
    using FieldsType = DynamicArray<DictField>;
    using SignalsType = DynamicArray<SignalBlock>;
    using MetaType = Optional<MetaData>;

    Impl():
        name_{},
        protocol_{},
        type_{},
        fields_{},
        signals_{},
        meta_{}
    {}

    Impl(NameType name,ProtocolType protocol,TypeType type,FieldsType fields,SignalsType signals,MetaType meta):
        name_{name},
        protocol_{protocol},
        type_{type},
        fields_{fields},
        signals_{signals},
        meta_{meta}
    {}

    static Impl FromJson(json j){
        return Impl {
            NameType::FromJson(j["name"]),
            ProtocolType::FromJson(j["protocol"]),
            TypeType::FromJson(j["type"]),
            FieldsType::FromJson(j["fields"]),
            SignalsType::FromJson(j["signals"]),
            MetaType::FromJson(j["meta"]),
        };
    }

    static Impl Decode(Buffer& buffer, Endianess endianess=Endianess::Little) {
        auto name = NameType::Decode(buffer, endianess);
        auto protocol = ProtocolType::Decode(buffer, endianess);
        auto type = TypeType::Decode(buffer, endianess);
        auto fields = FieldsType::Decode(buffer, endianess);
        auto signals = SignalsType::Decode(buffer, endianess);
        auto meta = MetaType::Decode(buffer, endianess);

        return Impl(name,protocol,type,fields,signals,meta);
    }

    template<typename Iterator>
    static Impl Decode(Iterator begin, Iterator end) {
        auto buffer = Buffer{begin, end};
        return Impl::Decode(buffer);
    }

    json DecodeJson() const {
        json j{};
        j["name"] = name_.DecodeJson();
        j["protocol"] = protocol_.DecodeJson();
        j["type"] = type_.DecodeJson();
        j["fields"] = fields_.DecodeJson();
        j["signals"] = signals_.DecodeJson();
        j["meta"] = meta_.DecodeJson();
        return j;
    }

    Buffer Encode(Endianess endianess=Endianess::Little) {
        Buffer buffer{0};
        Encode(buffer, endianess);
        return buffer;
    }

    void Encode(Buffer& buffer, Endianess endianess=Endianess::Little) const {
        name_.Encode(buffer, endianess);
        protocol_.Encode(buffer, endianess);
        type_.Encode(buffer, endianess);
        fields_.Encode(buffer, endianess);
        signals_.Encode(buffer, endianess);
        meta_.Encode(buffer, endianess);
    }
    NameType GetName() const {
        return name_;
    }
    ProtocolType GetProtocol() const {
        return protocol_;
    }
    TypeType GetType() const {
        return type_;
    }
    FieldsType GetFields() const {
        return fields_;
    }
    SignalsType GetSignals() const {
        return signals_;
    }
    MetaType GetMeta() const {
        return meta_;
    }
    NameType& ViewName() {
        return name_;
    }
    ProtocolType& ViewProtocol() {
        return protocol_;
    }
    TypeType& ViewType() {
        return type_;
    }
    FieldsType& ViewFields() {
        return fields_;
    }
    SignalsType& ViewSignals() {
        return signals_;
    }
    MetaType& ViewMeta() {
        return meta_;
    }
    inline bool operator==(const Impl& rhs) const {
        return  name_ == rhs.GetName()
        	&& protocol_ == rhs.GetProtocol()
        	&& type_ == rhs.GetType()
        	&& fields_ == rhs.GetFields()
        	&& signals_ == rhs.GetSignals()
        	&& meta_ == rhs.GetMeta();
    }

    std::string ToString(std::string prefix = "") const {
        std::stringstream ss{};
        auto p = prefix + "\t";
        ss << "Impl {" << std::endl;
        ss << p << "name: " << name_.ToString(p) << std::endl;
        ss << p << "protocol: " << protocol_.ToString(p) << std::endl;
        ss << p << "type: " << type_.ToString(p) << std::endl;
        ss << p << "fields: " << fields_.ToString(p) << std::endl;
        ss << p << "signals: " << signals_.ToString(p) << std::endl;
        ss << p << "meta: " << meta_.ToString(p) << std::endl;
        ss << prefix << "}" << std::endl;
        return ss.str();
    }

private:
    NameType name_;
    ProtocolType protocol_;
    TypeType type_;
    FieldsType fields_;
    SignalsType signals_;
    MetaType meta_;
};


struct Method {
    using NameType = String;
    using IdType = Unsigned<std::uint32_t, 32>;
    using InputType = String;
    using OutputType = String;
    using MetaType = Optional<MetaData>;

    Method():
        name_{},
        id_{},
        input_{},
        output_{},
        meta_{}
    {}

    Method(NameType name,IdType id,InputType input,OutputType output,MetaType meta):
        name_{name},
        id_{id},
        input_{input},
        output_{output},
        meta_{meta}
    {}

    static Method FromJson(json j){
        return Method {
            NameType::FromJson(j["name"]),
            IdType::FromJson(j["id"]),
            InputType::FromJson(j["input"]),
            OutputType::FromJson(j["output"]),
            MetaType::FromJson(j["meta"]),
        };
    }

    static Method Decode(Buffer& buffer, Endianess endianess=Endianess::Little) {
        auto name = NameType::Decode(buffer, endianess);
        auto id = IdType::Decode(buffer, endianess);
        auto input = InputType::Decode(buffer, endianess);
        auto output = OutputType::Decode(buffer, endianess);
        auto meta = MetaType::Decode(buffer, endianess);

        return Method(name,id,input,output,meta);
    }

    template<typename Iterator>
    static Method Decode(Iterator begin, Iterator end) {
        auto buffer = Buffer{begin, end};
        return Method::Decode(buffer);
    }

    json DecodeJson() const {
        json j{};
        j["name"] = name_.DecodeJson();
        j["id"] = id_.DecodeJson();
        j["input"] = input_.DecodeJson();
        j["output"] = output_.DecodeJson();
        j["meta"] = meta_.DecodeJson();
        return j;
    }

    Buffer Encode(Endianess endianess=Endianess::Little) {
        Buffer buffer{0};
        Encode(buffer, endianess);
        return buffer;
    }

    void Encode(Buffer& buffer, Endianess endianess=Endianess::Little) const {
        name_.Encode(buffer, endianess);
        id_.Encode(buffer, endianess);
        input_.Encode(buffer, endianess);
        output_.Encode(buffer, endianess);
        meta_.Encode(buffer, endianess);
    }
    NameType GetName() const {
        return name_;
    }
    IdType GetId() const {
        return id_;
    }
    InputType GetInput() const {
        return input_;
    }
    OutputType GetOutput() const {
        return output_;
    }
    MetaType GetMeta() const {
        return meta_;
    }
    NameType& ViewName() {
        return name_;
    }
    IdType& ViewId() {
        return id_;
    }
    InputType& ViewInput() {
        return input_;
    }
    OutputType& ViewOutput() {
        return output_;
    }
    MetaType& ViewMeta() {
        return meta_;
    }
    inline bool operator==(const Method& rhs) const {
        return  name_ == rhs.GetName()
        	&& id_ == rhs.GetId()
        	&& input_ == rhs.GetInput()
        	&& output_ == rhs.GetOutput()
        	&& meta_ == rhs.GetMeta();
    }

    std::string ToString(std::string prefix = "") const {
        std::stringstream ss{};
        auto p = prefix + "\t";
        ss << "Method {" << std::endl;
        ss << p << "name: " << name_.ToString(p) << std::endl;
        ss << p << "id: " << id_.ToString(p) << std::endl;
        ss << p << "input: " << input_.ToString(p) << std::endl;
        ss << p << "output: " << output_.ToString(p) << std::endl;
        ss << p << "meta: " << meta_.ToString(p) << std::endl;
        ss << prefix << "}" << std::endl;
        return ss.str();
    }

private:
    NameType name_;
    IdType id_;
    InputType input_;
    OutputType output_;
    MetaType meta_;
};


struct Service {
    using NameType = String;
    using IdType = Unsigned<std::uint32_t, 32>;
    using MethodsType = DynamicArray<Method>;
    using MetaType = Optional<MetaData>;

    Service():
        name_{},
        id_{},
        methods_{},
        meta_{}
    {}

    Service(NameType name,IdType id,MethodsType methods,MetaType meta):
        name_{name},
        id_{id},
        methods_{methods},
        meta_{meta}
    {}

    static Service FromJson(json j){
        return Service {
            NameType::FromJson(j["name"]),
            IdType::FromJson(j["id"]),
            MethodsType::FromJson(j["methods"]),
            MetaType::FromJson(j["meta"]),
        };
    }

    static Service Decode(Buffer& buffer, Endianess endianess=Endianess::Little) {
        auto name = NameType::Decode(buffer, endianess);
        auto id = IdType::Decode(buffer, endianess);
        auto methods = MethodsType::Decode(buffer, endianess);
        auto meta = MetaType::Decode(buffer, endianess);

        return Service(name,id,methods,meta);
    }

    template<typename Iterator>
    static Service Decode(Iterator begin, Iterator end) {
        auto buffer = Buffer{begin, end};
        return Service::Decode(buffer);
    }

    json DecodeJson() const {
        json j{};
        j["name"] = name_.DecodeJson();
        j["id"] = id_.DecodeJson();
        j["methods"] = methods_.DecodeJson();
        j["meta"] = meta_.DecodeJson();
        return j;
    }

    Buffer Encode(Endianess endianess=Endianess::Little) {
        Buffer buffer{0};
        Encode(buffer, endianess);
        return buffer;
    }

    void Encode(Buffer& buffer, Endianess endianess=Endianess::Little) const {
        name_.Encode(buffer, endianess);
        id_.Encode(buffer, endianess);
        methods_.Encode(buffer, endianess);
        meta_.Encode(buffer, endianess);
    }
    NameType GetName() const {
        return name_;
    }
    IdType GetId() const {
        return id_;
    }
    MethodsType GetMethods() const {
        return methods_;
    }
    MetaType GetMeta() const {
        return meta_;
    }
    NameType& ViewName() {
        return name_;
    }
    IdType& ViewId() {
        return id_;
    }
    MethodsType& ViewMethods() {
        return methods_;
    }
    MetaType& ViewMeta() {
        return meta_;
    }
    inline bool operator==(const Service& rhs) const {
        return  name_ == rhs.GetName()
        	&& id_ == rhs.GetId()
        	&& methods_ == rhs.GetMethods()
        	&& meta_ == rhs.GetMeta();
    }

    std::string ToString(std::string prefix = "") const {
        std::stringstream ss{};
        auto p = prefix + "\t";
        ss << "Service {" << std::endl;
        ss << p << "name: " << name_.ToString(p) << std::endl;
        ss << p << "id: " << id_.ToString(p) << std::endl;
        ss << p << "methods: " << methods_.ToString(p) << std::endl;
        ss << p << "meta: " << meta_.ToString(p) << std::endl;
        ss << prefix << "}" << std::endl;
        return ss.str();
    }

private:
    NameType name_;
    IdType id_;
    MethodsType methods_;
    MetaType meta_;
};


struct Fcp {
    using StructsType = DynamicArray<Struct>;
    using EnumsType = DynamicArray<Enum>;
    using ImplsType = DynamicArray<Impl>;
    using ServicesType = DynamicArray<Service>;
    using VersionType = String;

    Fcp():
        structs_{},
        enums_{},
        impls_{},
        services_{},
        version_{}
    {}

    Fcp(StructsType structs,EnumsType enums,ImplsType impls,ServicesType services,VersionType version):
        structs_{structs},
        enums_{enums},
        impls_{impls},
        services_{services},
        version_{version}
    {}

    static Fcp FromJson(json j){
        return Fcp {
            StructsType::FromJson(j["structs"]),
            EnumsType::FromJson(j["enums"]),
            ImplsType::FromJson(j["impls"]),
            ServicesType::FromJson(j["services"]),
            VersionType::FromJson(j["version"]),
        };
    }

    static Fcp Decode(Buffer& buffer, Endianess endianess=Endianess::Little) {
        auto structs = StructsType::Decode(buffer, endianess);
        auto enums = EnumsType::Decode(buffer, endianess);
        auto impls = ImplsType::Decode(buffer, endianess);
        auto services = ServicesType::Decode(buffer, endianess);
        auto version = VersionType::Decode(buffer, endianess);

        return Fcp(structs,enums,impls,services,version);
    }

    template<typename Iterator>
    static Fcp Decode(Iterator begin, Iterator end) {
        auto buffer = Buffer{begin, end};
        return Fcp::Decode(buffer);
    }

    json DecodeJson() const {
        json j{};
        j["structs"] = structs_.DecodeJson();
        j["enums"] = enums_.DecodeJson();
        j["impls"] = impls_.DecodeJson();
        j["services"] = services_.DecodeJson();
        j["version"] = version_.DecodeJson();
        return j;
    }

    Buffer Encode(Endianess endianess=Endianess::Little) {
        Buffer buffer{0};
        Encode(buffer, endianess);
        return buffer;
    }

    void Encode(Buffer& buffer, Endianess endianess=Endianess::Little) const {
        structs_.Encode(buffer, endianess);
        enums_.Encode(buffer, endianess);
        impls_.Encode(buffer, endianess);
        services_.Encode(buffer, endianess);
        version_.Encode(buffer, endianess);
    }
    StructsType GetStructs() const {
        return structs_;
    }
    EnumsType GetEnums() const {
        return enums_;
    }
    ImplsType GetImpls() const {
        return impls_;
    }
    ServicesType GetServices() const {
        return services_;
    }
    VersionType GetVersion() const {
        return version_;
    }
    StructsType& ViewStructs() {
        return structs_;
    }
    EnumsType& ViewEnums() {
        return enums_;
    }
    ImplsType& ViewImpls() {
        return impls_;
    }
    ServicesType& ViewServices() {
        return services_;
    }
    VersionType& ViewVersion() {
        return version_;
    }
    inline bool operator==(const Fcp& rhs) const {
        return  structs_ == rhs.GetStructs()
        	&& enums_ == rhs.GetEnums()
        	&& impls_ == rhs.GetImpls()
        	&& services_ == rhs.GetServices()
        	&& version_ == rhs.GetVersion();
    }

    std::string ToString(std::string prefix = "") const {
        std::stringstream ss{};
        auto p = prefix + "\t";
        ss << "Fcp {" << std::endl;
        ss << p << "structs: " << structs_.ToString(p) << std::endl;
        ss << p << "enums: " << enums_.ToString(p) << std::endl;
        ss << p << "impls: " << impls_.ToString(p) << std::endl;
        ss << p << "services: " << services_.ToString(p) << std::endl;
        ss << p << "version: " << version_.ToString(p) << std::endl;
        ss << prefix << "}" << std::endl;
        return ss.str();
    }

private:
    StructsType structs_;
    EnumsType enums_;
    ImplsType impls_;
    ServicesType services_;
    VersionType version_;
};


struct StaticSchema: public ISchema
{
    StaticSchema() = default;

    std::optional<json> DecodeJson(std::string name, std::vector<std::uint8_t> data, std::string bus="default") override {
        auto buffer = Buffer{data.begin(), data.end()};
        if (name == "MetaData" && bus == "default") {
            return MetaData::Decode(buffer).DecodeJson();
        }
        if (name == "Type" && bus == "default") {
            return Type::Decode(buffer).DecodeJson();
        }
        if (name == "StructField" && bus == "default") {
            return StructField::Decode(buffer).DecodeJson();
        }
        if (name == "Struct" && bus == "default") {
            return Struct::Decode(buffer).DecodeJson();
        }
        if (name == "Enumeration" && bus == "default") {
            return Enumeration::Decode(buffer).DecodeJson();
        }
        if (name == "Enum" && bus == "default") {
            return Enum::Decode(buffer).DecodeJson();
        }
        if (name == "DictField" && bus == "default") {
            return DictField::Decode(buffer).DecodeJson();
        }
        if (name == "SignalBlock" && bus == "default") {
            return SignalBlock::Decode(buffer).DecodeJson();
        }
        if (name == "Impl" && bus == "default") {
            return Impl::Decode(buffer).DecodeJson();
        }
        if (name == "Method" && bus == "default") {
            return Method::Decode(buffer).DecodeJson();
        }
        if (name == "Service" && bus == "default") {
            return Service::Decode(buffer).DecodeJson();
        }
        if (name == "Fcp" && bus == "default") {
            return Fcp::Decode(buffer).DecodeJson();
        }

        return std::nullopt;
    }

    std::optional<std::vector<std::uint8_t>> EncodeJson(std::string msg_name, json j) {
        if (msg_name == "MetaData") {
            auto s = MetaData::FromJson(j);
            return s.Encode().GetData();
        }
        if (msg_name == "Type") {
            auto s = Type::FromJson(j);
            return s.Encode().GetData();
        }
        if (msg_name == "StructField") {
            auto s = StructField::FromJson(j);
            return s.Encode().GetData();
        }
        if (msg_name == "Struct") {
            auto s = Struct::FromJson(j);
            return s.Encode().GetData();
        }
        if (msg_name == "Enumeration") {
            auto s = Enumeration::FromJson(j);
            return s.Encode().GetData();
        }
        if (msg_name == "Enum") {
            auto s = Enum::FromJson(j);
            return s.Encode().GetData();
        }
        if (msg_name == "DictField") {
            auto s = DictField::FromJson(j);
            return s.Encode().GetData();
        }
        if (msg_name == "SignalBlock") {
            auto s = SignalBlock::FromJson(j);
            return s.Encode().GetData();
        }
        if (msg_name == "Impl") {
            auto s = Impl::FromJson(j);
            return s.Encode().GetData();
        }
        if (msg_name == "Method") {
            auto s = Method::FromJson(j);
            return s.Encode().GetData();
        }
        if (msg_name == "Service") {
            auto s = Service::FromJson(j);
            return s.Encode().GetData();
        }
        if (msg_name == "Fcp") {
            auto s = Fcp::FromJson(j);
            return s.Encode().GetData();
        }

        return std::nullopt;
    }
};

} // reflection
} // namespace fcp