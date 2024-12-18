#include "can_signal_parser.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

#ifdef __cplusplus
extern "C" {
#endif

/** @def get_bit(word, pos) (word >> pos) & 0x1
 * Get a bit from a bitfield
 */
#define get_bit(word, pos) (word >> pos) & 0x1

/** @def can_word(msg) (*((uint64_t *) (msg->data)))
 *  Convert CanFrame to uint64_t word with data contents.
 */
#define can_word(msg) (*((uint64_t *)(msg->data)))

#define cast_double(ptr) *((double *)(ptr))
#define cast_float(ptr) *((float *)(ptr))
#define get_bitfield(data, start, length) (((data) >> (start)) & bitmask(length))
#define set_bitfield(data, start, length) ((((uint64_t)data & bitmask(length)) << start))

typedef union {
    float f;
    uint32_t i;
} u_f32;

typedef union {
    double d;
    uint64_t i;
} u_f64;

typedef enum { U8, U16, U32, U64, I8, I16, I32, I64 } IntType;

u_f32 set_bitfield_float(float data, uint8_t start, uint8_t length) {
    u_f32 d = {.f = (data)};
    d.i = ((d.i & bitmask(length)) << (start));

    return d;
}

u_f64 set_bitfield_double(double data, uint8_t start, uint8_t length) {
    u_f64 d = {.d = (data)};
    d.i = ((d.i & bitmask(length)) << (start));

    return d;
}

uint64_t apply_linear_uint64_t(uint64_t bitfield, float scale, float offset);
int64_t apply_linear_int64_t(int64_t bitfield, float scale, float offset);
double apply_linear_double(double bitfield, float scale, float offset);
float apply_linear_float(float bitfield, float scale, float offset);
int64_t bitfield_sign_conv(uint64_t bitfield, uint8_t length);

uint16_t swap_uint16(uint16_t val) { return (val << 8) | (val >> 8); }

int16_t swap_int16(int16_t val) { return (val << 8) | ((val >> 8) & 0xFF); }

uint32_t swap_uint32(uint32_t val) {
    val = ((val << 8) & 0xFF00FF00) | ((val >> 8) & 0xFF00FF);
    return (val << 16) | (val >> 16);
}

int32_t swap_int32(int32_t val) {
    val = ((val << 8) & 0xFF00FF00) | ((val >> 8) & 0xFF00FF);
    return (val << 16) | ((val >> 16) & 0xFFFF);
}

int64_t swap_int64(int64_t val) {
    val = ((val << 8) & 0xFF00FF00FF00FF00ULL) | ((val >> 8) & 0x00FF00FF00FF00FFULL);
    val = ((val << 16) & 0xFFFF0000FFFF0000ULL) | ((val >> 16) & 0x0000FFFF0000FFFFULL);
    return (val << 32) | ((val >> 32) & 0xFFFFFFFFULL);
}

uint64_t swap_uint64(uint64_t val) {
    val = ((val << 8) & 0xFF00FF00FF00FF00ULL) | ((val >> 8) & 0x00FF00FF00FF00FFULL);
    val = ((val << 16) & 0xFFFF0000FFFF0000ULL) | ((val >> 16) & 0x0000FFFF0000FFFFULL);
    return (val << 32) | (val >> 32);
}

uint64_t swap_bytes_int(uint64_t val, IntType type) {
    switch (type) {
        case U8:
            return val;
        case U16:
            return swap_uint16((uint16_t)val);
        case U32:
            return swap_uint32((uint32_t)val);
        case U64:
            return swap_uint64(val);
        case I8:
            return val;
        case I16:
            return swap_int16((int16_t)val);
        case I32:
            return swap_int32((int32_t)val);
        case I64:
            return swap_int64((int64_t)val);
    }
}

/** @fn uint64_t bitmask(uint8_t length)
 *  @brief Generate a bitmask with length bits
 * set to 1.
 *  @param length Size of the bit mask
 */
uint64_t bitmask(uint8_t length) {
    static const uint64_t bitmask_table[65] = {
        0x0000000000000000ULL, 0x0000000000000001ULL, 0x0000000000000003ULL, 0x0000000000000007ULL,
        0x000000000000000fULL, 0x000000000000001fULL, 0x000000000000003fULL, 0x000000000000007fULL,
        0x00000000000000ffULL, 0x00000000000001ffULL, 0x00000000000003ffULL, 0x00000000000007ffULL,
        0x0000000000000fffULL, 0x0000000000001fffULL, 0x0000000000003fffULL, 0x0000000000007fffULL,
        0x000000000000ffffULL, 0x000000000001ffffULL, 0x000000000003ffffULL, 0x000000000007ffffULL,
        0x00000000000fffffULL, 0x00000000001fffffULL, 0x00000000003fffffULL, 0x00000000007fffffULL,
        0x0000000000ffffffULL, 0x0000000001ffffffULL, 0x0000000003ffffffULL, 0x0000000007ffffffULL,
        0x000000000fffffffULL, 0x000000001fffffffULL, 0x000000003fffffffULL, 0x000000007fffffffULL,
        0x00000000ffffffffULL, 0x00000001ffffffffULL, 0x00000003ffffffffULL, 0x00000007ffffffffULL,
        0x0000000fffffffffULL, 0x0000001fffffffffULL, 0x0000003fffffffffULL, 0x0000007fffffffffULL,
        0x000000ffffffffffULL, 0x000001ffffffffffULL, 0x000003ffffffffffULL, 0x000007ffffffffffULL,
        0x00000fffffffffffULL, 0x00001fffffffffffULL, 0x00003fffffffffffULL, 0x00007fffffffffffULL,
        0x0000ffffffffffffULL, 0x0001ffffffffffffULL, 0x0003ffffffffffffULL, 0x0007ffffffffffffULL,
        0x000fffffffffffffULL, 0x001fffffffffffffULL, 0x003fffffffffffffULL, 0x007fffffffffffffULL,
        0x00ffffffffffffffULL, 0x01ffffffffffffffULL, 0x03ffffffffffffffULL, 0x07ffffffffffffffULL,
        0x0fffffffffffffffULL, 0x1fffffffffffffffULL, 0x3fffffffffffffffULL, 0x7fffffffffffffffULL,
        0xffffffffffffffffULL};

    if (length < (sizeof(bitmask_table) / sizeof(bitmask_table[0])))
        return bitmask_table[length];
    else
        return 0xffffffffffffffffULL;
}

/** @fn uint64_t apply_linear_uint64_t(uint64_t
 * bitfield, float scale, double offset)
 *  @brief apply a linear conversion to a 64 bit
 * uint8_t number.
 *  @param bitfield 64 bit uint8_t data
 *  @param scale Scaling to apply
 *  @param offset Offset to apply
 */
uint64_t apply_linear_uint64_t(uint64_t bitfield, float scale, float offset) {
    if (scale == 1.0) {
        return bitfield + (uint64_t)offset;
    } else {
        return scale * (uint32_t)bitfield + offset;
    }
}

/** @fn int64_t apply_linear_int64_t(int64_t
 * bitfield, float scale, double offset)
 *  @brief apply a linear conversion to a 64 bit
 * signed number. Only applies transformations
 * for numbers up to 32 bit
 *  @param bitfield 64 bit signed data.
 *  @param scale Scaling to apply.
 *  @param offset Offset to apply.
 */
int64_t apply_linear_int64_t(int64_t bitfield, float scale, float offset) {
    if (scale == 1.0) {
        return bitfield + (int64_t)offset;
    }

    else {
        return scale * (int32_t)bitfield + offset;
    }
}

/** @fn double apply_linear_double(double
 * bitfield, float scale, float offset, bool
 * is_big_endian)
 *  @brief apply a linear conversion to a
 * double.
 *  @param bitfield double.
 *  @param scale Scaling to apply.
 *  @param offset Offset to apply.
 */
double apply_linear_double(double bitfield, float scale, float offset) {
    return scale * bitfield + offset;
}

/** @fn float apply_linear_float(float bitfield,
 * float scale, float offset, bool
 * is_big_endian)
 *  @brief apply a linear conversion to a float.
 *  @param bitfield float.
 *  @param scale Scaling to apply.
 *  @param offset Offset to apply.
 */
float apply_linear_float(float bitfield, float scale, float offset) {
    return scale * bitfield + offset;
}

/** @fn int64_t bitfield_sign_conv(uint64_t
 * bitfield, uint8_t length)
 *  @brief change sign of a 64 bit signed number
 *  @param bitfield The number.
 *  @param length Size of the number
 */
int64_t bitfield_sign_conv(uint64_t bitfield, uint8_t length) {
    if (get_bit(bitfield, (length - 1))) {
        return (int64_t)((0xFFFFFFFFFFFFFFFFUL << length) | (bitfield));
    } else {
        return (int64_t)bitfield;
    }
}

uint64_t can_decode_signal_as_uint64_t(const CanFrame *msg, uint32_t start, uint32_t length,
                                       float scale, float offset, bool is_big_endian) {
    uint64_t bitfield = get_bitfield(can_word(msg), start, length);
    if (is_big_endian) bitfield = swap_bytes_int(bitfield, U64);

    return apply_linear_uint64_t(bitfield, scale, offset);
}

uint64_t can_encode_signal_from_uint64_t(uint64_t signal, uint32_t start, uint32_t length,
                                         float scale, float offset, bool is_big_endian) {
    uint64_t bitfield =
        set_bitfield(apply_linear_uint64_t(signal, 1 / scale, -offset), start, length);

    return is_big_endian ? swap_bytes_int(bitfield, U64) : bitfield;
}

uint32_t can_decode_signal_as_uint32_t(const CanFrame *msg, uint32_t start, uint32_t length,
                                       float scale, float offset, bool is_big_endian) {
    uint32_t bitfield = (uint32_t)get_bitfield(can_word(msg), start, length);
    if (is_big_endian) bitfield = swap_bytes_int(bitfield, U32);

    return apply_linear_uint64_t(bitfield, scale, offset);
}

uint64_t can_encode_signal_from_uint32_t(uint32_t signal, uint32_t start, uint32_t length,
                                         float scale, float offset, bool is_big_endian) {
    uint64_t bitfield =
        set_bitfield(apply_linear_uint64_t(signal, 1 / scale, -offset), start, length);

    return is_big_endian ? swap_bytes_int(bitfield, U32) : bitfield;
}

uint16_t can_decode_signal_as_uint16_t(const CanFrame *msg, uint32_t start, uint32_t length,
                                       float scale, float offset, bool is_big_endian) {
    uint16_t bitfield = (uint16_t)get_bitfield(can_word(msg), start, length);
    if (is_big_endian) bitfield = swap_bytes_int(bitfield, U16);

    return apply_linear_uint64_t(bitfield, scale, offset);
}

uint64_t can_encode_signal_from_uint16_t(uint16_t signal, uint32_t start, uint32_t length,
                                         float scale, float offset, bool is_big_endian) {
    uint64_t bitfield =
        set_bitfield(apply_linear_uint64_t(signal, 1 / scale, -offset), start, length);

    return is_big_endian ? swap_bytes_int(bitfield, U16) : bitfield;
}

uint8_t can_decode_signal_as_uint8_t(const CanFrame *msg, uint32_t start, uint32_t length,
                                     float scale, float offset, bool is_big_endian) {
    uint8_t bitfield = (uint8_t)get_bitfield(can_word(msg), start, length);
    if (is_big_endian) bitfield = swap_bytes_int(bitfield, U8);

    return apply_linear_uint64_t(bitfield, scale, offset);
}

uint64_t can_encode_signal_from_uint8_t(uint8_t signal, uint32_t start, uint32_t length,
                                        float scale, float offset, bool is_big_endian) {
    uint64_t bitfield =
        set_bitfield(apply_linear_uint64_t(signal, 1 / scale, -offset), start, length);

    return is_big_endian ? swap_bytes_int(bitfield, U8) : bitfield;
}

/* Only works up to 32 bit */
double can_decode_signal_as_double(const CanFrame *msg, uint32_t start, uint32_t length,
                                   float scale, float offset, bool is_big_endian) {
    u_f64 bitfield;
    memcpy(&bitfield.i, msg->data, 8);
    if (is_big_endian) bitfield.i = swap_bytes_int(bitfield.i, U64);

    return apply_linear_double(bitfield.d, scale, offset);
}

uint64_t can_encode_signal_from_double(double signal, uint32_t start, uint32_t length, float scale,
                                       float offset, bool is_big_endian) {
    u_f64 bitfield =
        set_bitfield_double(apply_linear_double(signal, 1 / scale, -offset), start, length);

    return is_big_endian ? swap_bytes_int(bitfield.i, U64) : bitfield.i;
}

/* Only works up to 32 bit */
float can_decode_signal_as_float(const CanFrame *msg, uint32_t start, uint32_t length, float scale,
                                 float offset, bool is_big_endian) {
    u_f32 bitfield = {.i = get_bitfield(can_word(msg), start, length)};
    if (is_big_endian) bitfield.i = swap_bytes_int(bitfield.i, U32);

    return apply_linear_float(bitfield.f, scale, offset);
}

uint64_t can_encode_signal_from_float(float signal, uint32_t start, uint32_t length, float scale,
                                      float offset, bool is_big_endian) {
    u_f32 bitfield =
        set_bitfield_float(apply_linear_float(signal, 1 / scale, -offset), start, length);

    return is_big_endian ? swap_bytes_int(bitfield.i, U32) : bitfield.i;
}

int64_t can_decode_signal_as_int64_t(const CanFrame *msg, uint32_t start, uint32_t length,
                                     float scale, float offset, bool is_big_endian) {
    int64_t bitfield = get_bitfield(can_word(msg), start, length);
    if (is_big_endian) bitfield = swap_bytes_int(bitfield, I64);

    return apply_linear_int64_t(bitfield, scale, offset);
}

uint64_t can_encode_signal_from_int64_t(int64_t signal, uint32_t start, uint32_t length,
                                        float scale, float offset, bool is_big_endian) {
    uint64_t bitfield =
        set_bitfield(apply_linear_int64_t(signal, 1 / scale, -offset), start, length);

    return is_big_endian ? swap_bytes_int(bitfield, I64) : bitfield;
}

int32_t can_decode_signal_as_int32_t(const CanFrame *msg, uint32_t start, uint32_t length,
                                     float scale, float offset, bool is_big_endian) {
    int64_t bitfield = bitfield_sign_conv(get_bitfield(can_word(msg), start, length), length);
    if (is_big_endian) bitfield = swap_bytes_int(bitfield, I32);

    return apply_linear_int64_t(bitfield, scale, offset);
}

uint64_t can_encode_signal_from_int32_t(int32_t signal, uint32_t start, uint32_t length,
                                        float scale, float offset, bool is_big_endian) {
    uint64_t bitfield =
        set_bitfield(apply_linear_int64_t(signal, 1 / scale, -offset), start, length);

    return is_big_endian ? swap_bytes_int(bitfield, I32) : bitfield;
}

int16_t can_decode_signal_as_int16_t(const CanFrame *msg, uint32_t start, uint32_t length,
                                     float scale, float offset, bool is_big_endian) {
    int64_t bitfield = bitfield_sign_conv(get_bitfield(can_word(msg), start, length), length);
    if (is_big_endian) bitfield = swap_bytes_int(bitfield, I16);

    return apply_linear_int64_t(bitfield, scale, offset);
}

uint64_t can_encode_signal_from_int16_t(int16_t signal, uint32_t start, uint32_t length,
                                        float scale, float offset, bool is_big_endian) {
    uint64_t bitfield =
        set_bitfield(apply_linear_int64_t(signal, 1 / scale, -offset), start, length);

    return is_big_endian ? swap_bytes_int(bitfield, I16) : bitfield;
}

int8_t can_decode_signal_as_int8_t(const CanFrame *msg, uint32_t start, uint32_t length,
                                   float scale, float offset, bool is_big_endian) {
    int64_t bitfield = bitfield_sign_conv(get_bitfield(can_word(msg), start, length), length);
    if (is_big_endian) bitfield = swap_bytes_int(bitfield, I8);

    return apply_linear_int64_t(bitfield, scale, offset);
}

uint64_t can_encode_signal_from_int8_t(int8_t signal, uint32_t start, uint32_t length, float scale,
                                       float offset, bool is_big_endian) {
    uint64_t bitfield =
        set_bitfield(apply_linear_int64_t(signal, 1 / scale, -offset), start, length);

    return is_big_endian ? swap_bytes_int(bitfield, I8) : bitfield;
}

float can_decode_signal_float_as_float(const CanFrame *msg, uint32_t start, uint32_t length,
                                       float scale, float offset, bool is_big_endian) {
    if (length != 32) {
        return 0.0f;
    }

    uint32_t word = (uint32_t)get_bitfield(can_word(msg), start, length);
    if (is_big_endian) word = swap_uint32(word);

    float f = *((float *)&word);
    return apply_linear_float(f, scale, offset);
}

uint64_t can_encode_signal_float_from_float(float signal, uint32_t start, uint32_t length,
                                            float scale, float offset, bool is_big_endian) {
    float d = apply_linear_float(signal, 1 / scale, -offset);
    uint32_t word = *(uint32_t *)&d;

    return is_big_endian ? swap_uint32(word) : word;
}

double can_decode_signal_double_as_double(const CanFrame *msg, uint32_t start, uint32_t length,
                                          float scale, float offset, bool is_big_endian) {
    if (length != 64) {
        return 0.0;
    }

    uint64_t word = get_bitfield(can_word(msg), start, length);
    if (is_big_endian) word = swap_uint64(word);

    double d = *((double *)&word);
    return apply_linear_double(d, scale, offset);
}

uint64_t can_encode_signal_double_from_double(double signal, uint32_t start, uint32_t length,
                                              float scale, float offset, bool is_big_endian) {
    double d = apply_linear_double(signal, 1 / scale, -offset);
    uint64_t word = *(uint64_t *)&d;

    return is_big_endian ? swap_uint64(word) : word;
}
#ifdef __cplusplus
}
#endif
