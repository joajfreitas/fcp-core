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
#include <sstream>
#include <algorithm>
#include <cstring>
#include <optional>

namespace fcp {

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

template<typename UnderlyingType, std::size_t BitSize>
class Unsigned {
public:
    Unsigned(): data_{0} {}
    Unsigned(UnderlyingType value): data_{value} {}

    static Unsigned Decode(Buffer& buffer) {
        auto word = buffer.get_word(BitSize);
        return Unsigned(static_cast<UnderlyingType>(word));
    }

    void _encode(Buffer& buffer) const {
        buffer.push_word<UnderlyingType, BitSize>(data_) ;
    }

    UnderlyingType GetData() const {
        return data_;
    }

    inline bool operator==(const Unsigned& rhs) const
    {
        return GetData() == rhs.GetData();
    }

    std::string to_string(std::string prefix = "") const {
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

    static Signed Decode(Buffer& buffer) {
        auto word = buffer.get_word(BitSize, true);
        return Signed(static_cast<UnderlyingType>(word));
    }

    void _encode(Buffer& buffer) const {
        buffer.push_word<UnderlyingType, BitSize>(data_) ;
    }

    UnderlyingType GetData() const {
        return data_;
    }

    inline bool operator==(const Signed& rhs) const
    {
        return GetData() == rhs.GetData();
    }

    std::string to_string(std::string prefix = "") const {
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

    static Float Decode(Buffer& buffer) {
        auto word = buffer.get_word(BitSize);

        UnderlyingType data{};
        std::memcpy(&data, &word, 4);

        return Float(data);
    }

    void _encode(Buffer& buffer) const {
        std::uint32_t tmp = 0;
        std::memcpy(&tmp, &data_, 4);
        buffer.push_word<std::uint32_t, BitSize>(tmp) ;
    }

    UnderlyingType GetData() const {
        return data_;
    }

    inline bool operator==(const Float& rhs) const
    {
        return GetData() == rhs.GetData();
    }

    std::string to_string(std::string prefix = "") const {
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

    static Double Decode(Buffer& buffer) {
        auto word = buffer.get_word(BitSize);

        UnderlyingType data{};
        std::memcpy(&data, &word, 8);

        return Double(data);
    }

    void _encode(Buffer& buffer) const {
        std::uint64_t tmp = 0;
        std::memcpy(&tmp, &data_, 8);
        buffer.push_word<std::uint64_t, BitSize>(tmp) ;
    }

    UnderlyingType GetData() const {
        return data_;
    }

    inline bool operator==(const Double& rhs) const
    {
        return GetData() == rhs.GetData();
    }


    std::string to_string(std::string prefix = "") const {
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

    static Array Decode(Buffer& buffer) {
        std::array<T, N> data{0};

        for (int i=0; i<N; i++) {
            data[i] = T::Decode(buffer);
        }

        return Array(data);
    }

    void _encode(Buffer& buffer) const {
        for (int i=0; i<N; i++) {
            data_[i]._encode(buffer);
        }
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


class String {
    public:

    String(): data_{} {}
    String(const std::string& value): data_{value} {}
    String(const char* value): data_{value} {}

    static String Decode(Buffer& buffer) {
        std::string data{};
        auto len = Unsigned<std::uint32_t, 32>::Decode(buffer).GetData();
        for (int i=0; i<len; i++) {
            data.push_back(Unsigned<std::uint8_t, 8>::Decode(buffer).GetData());
        }

        return String(data);
    }

    void _encode(Buffer& buffer) const {
        Unsigned<std::uint32_t, 32>(data_.size())._encode(buffer);
        for (const auto& c: data_) {
            Unsigned<std::uint8_t, 8>(c)._encode(buffer);
        }
    }

    std::string GetData() const {
        return data_;
    }

    inline bool operator==(const String& rhs) const
    {
        return GetData() == rhs.GetData();
    }

    std::string to_string(std::string prefix="") const {
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

    static DynamicArray Decode(Buffer& buffer) {
        std::vector<T> data{};
        auto len = Unsigned<std::uint32_t, 32>::Decode(buffer).GetData();
        for (int i=0; i<len; i++) {
            data.push_back(T::Decode(buffer));
        }

        return DynamicArray(data);
    }

    void _encode(Buffer& buffer) const {
        Unsigned<std::uint32_t, 32>(data_.size())._encode(buffer);
        for (auto x: data_) {
            x._encode(buffer);
        }
    }

    std::vector<T> GetData() const {
        return data_;
    }

    inline bool operator==(const DynamicArray& rhs) const
    {
        return GetData() == rhs.GetData();
    }

    std::string to_string(std::string prefix="") const {
        std::stringstream ss{};
        ss << "[";
        for (int i=0; i<data_.size(); i++) {
            ss << data_[i].to_string();
            if (i != data_.size()-1) {
                ss << data_[i].to_string() << ", ";
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

    Optional(): data_{} {}
    Optional(const std::optional<T>& value): data_{value} {}

    static Optional None() {
        return Optional(std::nullopt);
    }

    static Optional Some(const T& value) {
        return Optional(value);
    }

    static Optional Decode(Buffer& buffer) {
        std::optional<T> data;
        auto is_some = Unsigned<std::uint8_t, 8>::Decode(buffer).GetData();

        if (is_some) {
            data = T::Decode(buffer);
        }
        else {
            data = std::nullopt;
        }

        return Optional(data);
    }

    void _encode(Buffer& buffer) const {
        Unsigned<std::uint8_t, 8>(data_.has_value() ? 1 : 0)._encode(buffer);

        if (data_.has_value()) {
            data_.value()._encode(buffer);
        }
    }

    std::optional<T> GetData() const {
        return data_;
    }

    inline bool operator==(const Optional& rhs) const
    {
        return GetData() == rhs.GetData();
    }

    std::string to_string(std::string prefix="") const {
        std::stringstream ss{};
        if (data_.has_value()) {
            ss << "Some(";
            ss << data_.value().to_string();
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


struct MetaData {
    using LineType = Signed<std::int32_t, 32>;
    using End_lineType = Signed<std::int32_t, 32>;
    using ColumnType = Signed<std::int32_t, 32>;
    using End_columnType = Signed<std::int32_t, 32>;
    using Start_posType = Signed<std::int32_t, 32>;
    using End_posType = Signed<std::int32_t, 32>;
    using FilenameType = String;

    MetaData(LineType line,End_lineType end_line,ColumnType column,End_columnType end_column,Start_posType start_pos,End_posType end_pos,FilenameType filename):
    line_{line},
    end_line_{end_line},
    column_{column},
    end_column_{end_column},
    start_pos_{start_pos},
    end_pos_{end_pos},
    filename_{filename}
    {}

    static MetaData Decode(Buffer& buffer) {
        auto line = LineType::Decode(buffer);
        auto end_line = End_lineType::Decode(buffer);
        auto column = ColumnType::Decode(buffer);
        auto end_column = End_columnType::Decode(buffer);
        auto start_pos = Start_posType::Decode(buffer);
        auto end_pos = End_posType::Decode(buffer);
        auto filename = FilenameType::Decode(buffer);

        return MetaData(line,end_line,column,end_column,start_pos,end_pos,filename);
    }

    template<typename Iterator>
    static MetaData Decode(Iterator begin, Iterator end) {
        auto buffer = Buffer{begin, end};
        return MetaData::Decode(buffer);
    }

    void _encode(Buffer& buffer) const {
        line_._encode(buffer);
        end_line_._encode(buffer);
        column_._encode(buffer);
        end_column_._encode(buffer);
        start_pos_._encode(buffer);
        end_pos_._encode(buffer);
        filename_._encode(buffer);
    }

    Buffer encode() {
        Buffer buffer{0};
        _encode(buffer);
        return buffer;
    }

    
    LineType GetLine() const {
        return line_;
    }
    
    End_lineType GetEnd_line() const {
        return end_line_;
    }
    
    ColumnType GetColumn() const {
        return column_;
    }
    
    End_columnType GetEnd_column() const {
        return end_column_;
    }
    
    Start_posType GetStart_pos() const {
        return start_pos_;
    }
    
    End_posType GetEnd_pos() const {
        return end_pos_;
    }
    
    FilenameType GetFilename() const {
        return filename_;
    }
    

    inline bool operator==(const MetaData& rhs) const {
        return  line_ == rhs.GetLine()
        	&& end_line_ == rhs.GetEnd_line()
        	&& column_ == rhs.GetColumn()
        	&& end_column_ == rhs.GetEnd_column()
        	&& start_pos_ == rhs.GetStart_pos()
        	&& end_pos_ == rhs.GetEnd_pos()
        	&& filename_ == rhs.GetFilename();
    }

    std::string to_string(std::string prefix = "") const {
        std::stringstream ss{};
        auto p = prefix + "\t";
        ss << "MetaData {" << std::endl;
        ss << p << "line: " << line_.to_string(p) << std::endl;
        ss << p << "end_line: " << end_line_.to_string(p) << std::endl;
        ss << p << "column: " << column_.to_string(p) << std::endl;
        ss << p << "end_column: " << end_column_.to_string(p) << std::endl;
        ss << p << "start_pos: " << start_pos_.to_string(p) << std::endl;
        ss << p << "end_pos: " << end_pos_.to_string(p) << std::endl;
        ss << p << "filename: " << filename_.to_string(p) << std::endl;
        ss << prefix << "}" << std::endl;
        return ss.str();
    }
private:
    LineType line_;
    End_lineType end_line_;
    ColumnType column_;
    End_columnType end_column_;
    Start_posType start_pos_;
    End_posType end_pos_;
    FilenameType filename_;
};

struct Type {
    using NameType = String;
    using SizeType = Unsigned<std::uint32_t, 32>;
    using TypeType = String;

    Type(NameType name,SizeType size,TypeType type):
    name_{name},
    size_{size},
    type_{type}
    {}

    static Type Decode(Buffer& buffer) {
        auto name = NameType::Decode(buffer);
        auto size = SizeType::Decode(buffer);
        auto type = TypeType::Decode(buffer);

        return Type(name,size,type);
    }

    template<typename Iterator>
    static Type Decode(Iterator begin, Iterator end) {
        auto buffer = Buffer{begin, end};
        return Type::Decode(buffer);
    }

    void _encode(Buffer& buffer) const {
        name_._encode(buffer);
        size_._encode(buffer);
        type_._encode(buffer);
    }

    Buffer encode() {
        Buffer buffer{0};
        _encode(buffer);
        return buffer;
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
    

    inline bool operator==(const Type& rhs) const {
        return  name_ == rhs.GetName()
        	&& size_ == rhs.GetSize()
        	&& type_ == rhs.GetType();
    }

    std::string to_string(std::string prefix = "") const {
        std::stringstream ss{};
        auto p = prefix + "\t";
        ss << "Type {" << std::endl;
        ss << p << "name: " << name_.to_string(p) << std::endl;
        ss << p << "size: " << size_.to_string(p) << std::endl;
        ss << p << "type: " << type_.to_string(p) << std::endl;
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
    using Field_idType = Unsigned<std::uint32_t, 32>;
    using TypeType = DynamicArray<Type>;
    using UnitType = Optional<String>;
    using Min_valueType = Optional<Double>;
    using Max_valueType = Optional<Double>;
    using MetaType = Optional<MetaData>;

    StructField(NameType name,Field_idType field_id,TypeType type,UnitType unit,Min_valueType min_value,Max_valueType max_value,MetaType meta):
    name_{name},
    field_id_{field_id},
    type_{type},
    unit_{unit},
    min_value_{min_value},
    max_value_{max_value},
    meta_{meta}
    {}

    static StructField Decode(Buffer& buffer) {
        auto name = NameType::Decode(buffer);
        auto field_id = Field_idType::Decode(buffer);
        auto type = TypeType::Decode(buffer);
        auto unit = UnitType::Decode(buffer);
        auto min_value = Min_valueType::Decode(buffer);
        auto max_value = Max_valueType::Decode(buffer);
        auto meta = MetaType::Decode(buffer);

        return StructField(name,field_id,type,unit,min_value,max_value,meta);
    }

    template<typename Iterator>
    static StructField Decode(Iterator begin, Iterator end) {
        auto buffer = Buffer{begin, end};
        return StructField::Decode(buffer);
    }

    void _encode(Buffer& buffer) const {
        name_._encode(buffer);
        field_id_._encode(buffer);
        type_._encode(buffer);
        unit_._encode(buffer);
        min_value_._encode(buffer);
        max_value_._encode(buffer);
        meta_._encode(buffer);
    }

    Buffer encode() {
        Buffer buffer{0};
        _encode(buffer);
        return buffer;
    }

    
    NameType GetName() const {
        return name_;
    }
    
    Field_idType GetField_id() const {
        return field_id_;
    }
    
    TypeType GetType() const {
        return type_;
    }
    
    UnitType GetUnit() const {
        return unit_;
    }
    
    Min_valueType GetMin_value() const {
        return min_value_;
    }
    
    Max_valueType GetMax_value() const {
        return max_value_;
    }
    
    MetaType GetMeta() const {
        return meta_;
    }
    

    inline bool operator==(const StructField& rhs) const {
        return  name_ == rhs.GetName()
        	&& field_id_ == rhs.GetField_id()
        	&& type_ == rhs.GetType()
        	&& unit_ == rhs.GetUnit()
        	&& min_value_ == rhs.GetMin_value()
        	&& max_value_ == rhs.GetMax_value()
        	&& meta_ == rhs.GetMeta();
    }

    std::string to_string(std::string prefix = "") const {
        std::stringstream ss{};
        auto p = prefix + "\t";
        ss << "StructField {" << std::endl;
        ss << p << "name: " << name_.to_string(p) << std::endl;
        ss << p << "field_id: " << field_id_.to_string(p) << std::endl;
        ss << p << "type: " << type_.to_string(p) << std::endl;
        ss << p << "unit: " << unit_.to_string(p) << std::endl;
        ss << p << "min_value: " << min_value_.to_string(p) << std::endl;
        ss << p << "max_value: " << max_value_.to_string(p) << std::endl;
        ss << p << "meta: " << meta_.to_string(p) << std::endl;
        ss << prefix << "}" << std::endl;
        return ss.str();
    }
private:
    NameType name_;
    Field_idType field_id_;
    TypeType type_;
    UnitType unit_;
    Min_valueType min_value_;
    Max_valueType max_value_;
    MetaType meta_;
};

struct Struct {
    using NameType = String;
    using FieldsType = DynamicArray<StructField>;
    using MetaType = Optional<MetaData>;

    Struct(NameType name,FieldsType fields,MetaType meta):
    name_{name},
    fields_{fields},
    meta_{meta}
    {}

    static Struct Decode(Buffer& buffer) {
        auto name = NameType::Decode(buffer);
        auto fields = FieldsType::Decode(buffer);
        auto meta = MetaType::Decode(buffer);

        return Struct(name,fields,meta);
    }

    template<typename Iterator>
    static Struct Decode(Iterator begin, Iterator end) {
        auto buffer = Buffer{begin, end};
        return Struct::Decode(buffer);
    }

    void _encode(Buffer& buffer) const {
        name_._encode(buffer);
        fields_._encode(buffer);
        meta_._encode(buffer);
    }

    Buffer encode() {
        Buffer buffer{0};
        _encode(buffer);
        return buffer;
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
    

    inline bool operator==(const Struct& rhs) const {
        return  name_ == rhs.GetName()
        	&& fields_ == rhs.GetFields()
        	&& meta_ == rhs.GetMeta();
    }

    std::string to_string(std::string prefix = "") const {
        std::stringstream ss{};
        auto p = prefix + "\t";
        ss << "Struct {" << std::endl;
        ss << p << "name: " << name_.to_string(p) << std::endl;
        ss << p << "fields: " << fields_.to_string(p) << std::endl;
        ss << p << "meta: " << meta_.to_string(p) << std::endl;
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

    Enumeration(NameType name,ValueType value,MetaType meta):
    name_{name},
    value_{value},
    meta_{meta}
    {}

    static Enumeration Decode(Buffer& buffer) {
        auto name = NameType::Decode(buffer);
        auto value = ValueType::Decode(buffer);
        auto meta = MetaType::Decode(buffer);

        return Enumeration(name,value,meta);
    }

    template<typename Iterator>
    static Enumeration Decode(Iterator begin, Iterator end) {
        auto buffer = Buffer{begin, end};
        return Enumeration::Decode(buffer);
    }

    void _encode(Buffer& buffer) const {
        name_._encode(buffer);
        value_._encode(buffer);
        meta_._encode(buffer);
    }

    Buffer encode() {
        Buffer buffer{0};
        _encode(buffer);
        return buffer;
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
    

    inline bool operator==(const Enumeration& rhs) const {
        return  name_ == rhs.GetName()
        	&& value_ == rhs.GetValue()
        	&& meta_ == rhs.GetMeta();
    }

    std::string to_string(std::string prefix = "") const {
        std::stringstream ss{};
        auto p = prefix + "\t";
        ss << "Enumeration {" << std::endl;
        ss << p << "name: " << name_.to_string(p) << std::endl;
        ss << p << "value: " << value_.to_string(p) << std::endl;
        ss << p << "meta: " << meta_.to_string(p) << std::endl;
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

    Enum(NameType name,EnumerationType enumeration,MetaType meta):
    name_{name},
    enumeration_{enumeration},
    meta_{meta}
    {}

    static Enum Decode(Buffer& buffer) {
        auto name = NameType::Decode(buffer);
        auto enumeration = EnumerationType::Decode(buffer);
        auto meta = MetaType::Decode(buffer);

        return Enum(name,enumeration,meta);
    }

    template<typename Iterator>
    static Enum Decode(Iterator begin, Iterator end) {
        auto buffer = Buffer{begin, end};
        return Enum::Decode(buffer);
    }

    void _encode(Buffer& buffer) const {
        name_._encode(buffer);
        enumeration_._encode(buffer);
        meta_._encode(buffer);
    }

    Buffer encode() {
        Buffer buffer{0};
        _encode(buffer);
        return buffer;
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
    

    inline bool operator==(const Enum& rhs) const {
        return  name_ == rhs.GetName()
        	&& enumeration_ == rhs.GetEnumeration()
        	&& meta_ == rhs.GetMeta();
    }

    std::string to_string(std::string prefix = "") const {
        std::stringstream ss{};
        auto p = prefix + "\t";
        ss << "Enum {" << std::endl;
        ss << p << "name: " << name_.to_string(p) << std::endl;
        ss << p << "enumeration: " << enumeration_.to_string(p) << std::endl;
        ss << p << "meta: " << meta_.to_string(p) << std::endl;
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

    DictField(NameType name,ValueType value):
    name_{name},
    value_{value}
    {}

    static DictField Decode(Buffer& buffer) {
        auto name = NameType::Decode(buffer);
        auto value = ValueType::Decode(buffer);

        return DictField(name,value);
    }

    template<typename Iterator>
    static DictField Decode(Iterator begin, Iterator end) {
        auto buffer = Buffer{begin, end};
        return DictField::Decode(buffer);
    }

    void _encode(Buffer& buffer) const {
        name_._encode(buffer);
        value_._encode(buffer);
    }

    Buffer encode() {
        Buffer buffer{0};
        _encode(buffer);
        return buffer;
    }

    
    NameType GetName() const {
        return name_;
    }
    
    ValueType GetValue() const {
        return value_;
    }
    

    inline bool operator==(const DictField& rhs) const {
        return  name_ == rhs.GetName()
        	&& value_ == rhs.GetValue();
    }

    std::string to_string(std::string prefix = "") const {
        std::stringstream ss{};
        auto p = prefix + "\t";
        ss << "DictField {" << std::endl;
        ss << p << "name: " << name_.to_string(p) << std::endl;
        ss << p << "value: " << value_.to_string(p) << std::endl;
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

    SignalBlock(NameType name,FieldsType fields,MetaType meta):
    name_{name},
    fields_{fields},
    meta_{meta}
    {}

    static SignalBlock Decode(Buffer& buffer) {
        auto name = NameType::Decode(buffer);
        auto fields = FieldsType::Decode(buffer);
        auto meta = MetaType::Decode(buffer);

        return SignalBlock(name,fields,meta);
    }

    template<typename Iterator>
    static SignalBlock Decode(Iterator begin, Iterator end) {
        auto buffer = Buffer{begin, end};
        return SignalBlock::Decode(buffer);
    }

    void _encode(Buffer& buffer) const {
        name_._encode(buffer);
        fields_._encode(buffer);
        meta_._encode(buffer);
    }

    Buffer encode() {
        Buffer buffer{0};
        _encode(buffer);
        return buffer;
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
    

    inline bool operator==(const SignalBlock& rhs) const {
        return  name_ == rhs.GetName()
        	&& fields_ == rhs.GetFields()
        	&& meta_ == rhs.GetMeta();
    }

    std::string to_string(std::string prefix = "") const {
        std::stringstream ss{};
        auto p = prefix + "\t";
        ss << "SignalBlock {" << std::endl;
        ss << p << "name: " << name_.to_string(p) << std::endl;
        ss << p << "fields: " << fields_.to_string(p) << std::endl;
        ss << p << "meta: " << meta_.to_string(p) << std::endl;
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

    Impl(NameType name,ProtocolType protocol,TypeType type,FieldsType fields,SignalsType signals,MetaType meta):
    name_{name},
    protocol_{protocol},
    type_{type},
    fields_{fields},
    signals_{signals},
    meta_{meta}
    {}

    static Impl Decode(Buffer& buffer) {
        auto name = NameType::Decode(buffer);
        auto protocol = ProtocolType::Decode(buffer);
        auto type = TypeType::Decode(buffer);
        auto fields = FieldsType::Decode(buffer);
        auto signals = SignalsType::Decode(buffer);
        auto meta = MetaType::Decode(buffer);

        return Impl(name,protocol,type,fields,signals,meta);
    }

    template<typename Iterator>
    static Impl Decode(Iterator begin, Iterator end) {
        auto buffer = Buffer{begin, end};
        return Impl::Decode(buffer);
    }

    void _encode(Buffer& buffer) const {
        name_._encode(buffer);
        protocol_._encode(buffer);
        type_._encode(buffer);
        fields_._encode(buffer);
        signals_._encode(buffer);
        meta_._encode(buffer);
    }

    Buffer encode() {
        Buffer buffer{0};
        _encode(buffer);
        return buffer;
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
    

    inline bool operator==(const Impl& rhs) const {
        return  name_ == rhs.GetName()
        	&& protocol_ == rhs.GetProtocol()
        	&& type_ == rhs.GetType()
        	&& fields_ == rhs.GetFields()
        	&& signals_ == rhs.GetSignals()
        	&& meta_ == rhs.GetMeta();
    }

    std::string to_string(std::string prefix = "") const {
        std::stringstream ss{};
        auto p = prefix + "\t";
        ss << "Impl {" << std::endl;
        ss << p << "name: " << name_.to_string(p) << std::endl;
        ss << p << "protocol: " << protocol_.to_string(p) << std::endl;
        ss << p << "type: " << type_.to_string(p) << std::endl;
        ss << p << "fields: " << fields_.to_string(p) << std::endl;
        ss << p << "signals: " << signals_.to_string(p) << std::endl;
        ss << p << "meta: " << meta_.to_string(p) << std::endl;
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

struct Rpc {
    using NameType = String;
    using InputType = String;
    using OutputType = String;
    using MetaType = Optional<MetaData>;

    Rpc(NameType name,InputType input,OutputType output,MetaType meta):
    name_{name},
    input_{input},
    output_{output},
    meta_{meta}
    {}

    static Rpc Decode(Buffer& buffer) {
        auto name = NameType::Decode(buffer);
        auto input = InputType::Decode(buffer);
        auto output = OutputType::Decode(buffer);
        auto meta = MetaType::Decode(buffer);

        return Rpc(name,input,output,meta);
    }

    template<typename Iterator>
    static Rpc Decode(Iterator begin, Iterator end) {
        auto buffer = Buffer{begin, end};
        return Rpc::Decode(buffer);
    }

    void _encode(Buffer& buffer) const {
        name_._encode(buffer);
        input_._encode(buffer);
        output_._encode(buffer);
        meta_._encode(buffer);
    }

    Buffer encode() {
        Buffer buffer{0};
        _encode(buffer);
        return buffer;
    }

    
    NameType GetName() const {
        return name_;
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
    

    inline bool operator==(const Rpc& rhs) const {
        return  name_ == rhs.GetName()
        	&& input_ == rhs.GetInput()
        	&& output_ == rhs.GetOutput()
        	&& meta_ == rhs.GetMeta();
    }

    std::string to_string(std::string prefix = "") const {
        std::stringstream ss{};
        auto p = prefix + "\t";
        ss << "Rpc {" << std::endl;
        ss << p << "name: " << name_.to_string(p) << std::endl;
        ss << p << "input: " << input_.to_string(p) << std::endl;
        ss << p << "output: " << output_.to_string(p) << std::endl;
        ss << p << "meta: " << meta_.to_string(p) << std::endl;
        ss << prefix << "}" << std::endl;
        return ss.str();
    }
private:
    NameType name_;
    InputType input_;
    OutputType output_;
    MetaType meta_;
};

struct Service {
    using NameType = String;
    using RpcsType = DynamicArray<Rpc>;
    using MetaType = Optional<MetaData>;

    Service(NameType name,RpcsType rpcs,MetaType meta):
    name_{name},
    rpcs_{rpcs},
    meta_{meta}
    {}

    static Service Decode(Buffer& buffer) {
        auto name = NameType::Decode(buffer);
        auto rpcs = RpcsType::Decode(buffer);
        auto meta = MetaType::Decode(buffer);

        return Service(name,rpcs,meta);
    }

    template<typename Iterator>
    static Service Decode(Iterator begin, Iterator end) {
        auto buffer = Buffer{begin, end};
        return Service::Decode(buffer);
    }

    void _encode(Buffer& buffer) const {
        name_._encode(buffer);
        rpcs_._encode(buffer);
        meta_._encode(buffer);
    }

    Buffer encode() {
        Buffer buffer{0};
        _encode(buffer);
        return buffer;
    }

    
    NameType GetName() const {
        return name_;
    }
    
    RpcsType GetRpcs() const {
        return rpcs_;
    }
    
    MetaType GetMeta() const {
        return meta_;
    }
    

    inline bool operator==(const Service& rhs) const {
        return  name_ == rhs.GetName()
        	&& rpcs_ == rhs.GetRpcs()
        	&& meta_ == rhs.GetMeta();
    }

    std::string to_string(std::string prefix = "") const {
        std::stringstream ss{};
        auto p = prefix + "\t";
        ss << "Service {" << std::endl;
        ss << p << "name: " << name_.to_string(p) << std::endl;
        ss << p << "rpcs: " << rpcs_.to_string(p) << std::endl;
        ss << p << "meta: " << meta_.to_string(p) << std::endl;
        ss << prefix << "}" << std::endl;
        return ss.str();
    }
private:
    NameType name_;
    RpcsType rpcs_;
    MetaType meta_;
};

struct Fcp {
    using StructsType = DynamicArray<Struct>;
    using EnumsType = DynamicArray<Enum>;
    using ImplsType = DynamicArray<Impl>;
    using ServicesType = DynamicArray<Service>;
    using VersionType = String;

    Fcp(StructsType structs,EnumsType enums,ImplsType impls,ServicesType services,VersionType version):
    structs_{structs},
    enums_{enums},
    impls_{impls},
    services_{services},
    version_{version}
    {}

    static Fcp Decode(Buffer& buffer) {
        auto structs = StructsType::Decode(buffer);
        auto enums = EnumsType::Decode(buffer);
        auto impls = ImplsType::Decode(buffer);
        auto services = ServicesType::Decode(buffer);
        auto version = VersionType::Decode(buffer);

        return Fcp(structs,enums,impls,services,version);
    }

    template<typename Iterator>
    static Fcp Decode(Iterator begin, Iterator end) {
        auto buffer = Buffer{begin, end};
        return Fcp::Decode(buffer);
    }

    void _encode(Buffer& buffer) const {
        structs_._encode(buffer);
        enums_._encode(buffer);
        impls_._encode(buffer);
        services_._encode(buffer);
        version_._encode(buffer);
    }

    Buffer encode() {
        Buffer buffer{0};
        _encode(buffer);
        return buffer;
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
    

    inline bool operator==(const Fcp& rhs) const {
        return  structs_ == rhs.GetStructs()
        	&& enums_ == rhs.GetEnums()
        	&& impls_ == rhs.GetImpls()
        	&& services_ == rhs.GetServices()
        	&& version_ == rhs.GetVersion();
    }

    std::string to_string(std::string prefix = "") const {
        std::stringstream ss{};
        auto p = prefix + "\t";
        ss << "Fcp {" << std::endl;
        ss << p << "structs: " << structs_.to_string(p) << std::endl;
        ss << p << "enums: " << enums_.to_string(p) << std::endl;
        ss << p << "impls: " << impls_.to_string(p) << std::endl;
        ss << p << "services: " << services_.to_string(p) << std::endl;
        ss << p << "version: " << version_.to_string(p) << std::endl;
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
} // namespace fcp

#endif // __FCP_CAN_H__