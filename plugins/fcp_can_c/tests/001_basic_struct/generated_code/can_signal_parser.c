#include "can_signal_parser.h"

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
#define get_bitfield(data, start, length)                                      \
    (((data) >> (start)) & bitmask(length))
#define set_bitfield(data, start, length)                                      \
    ((((uint64_t)data & bitmask(length)) << start))

uint64_t apply_linear_uint64_t(uint64_t bitfield, double scale, double offset);
int64_t apply_linear_int64_t(int64_t bitfield, double scale, double offset);
double apply_linear_double(double bitfield, double scale, double offset);
float apply_linear_float(float bitfield, double scale, double offset);
int64_t bitfield_sign_conv(uint64_t bitfield, unsigned length);

/** @fn uint64_t bitmask(unsigned length)
 *  @brief Generate a bitmask with length bits set to 1.
 *  @param length Size of the bit mask
 */
uint64_t bitmask(unsigned length) {

    static const uint64_t bitmask_table[65] = {
        0x0000000000000000ULL, 0x0000000000000001ULL, 0x0000000000000003ULL,
        0x0000000000000007ULL, 0x000000000000000fULL, 0x000000000000001fULL,
        0x000000000000003fULL, 0x000000000000007fULL, 0x00000000000000ffULL,
        0x00000000000001ffULL, 0x00000000000003ffULL, 0x00000000000007ffULL,
        0x0000000000000fffULL, 0x0000000000001fffULL, 0x0000000000003fffULL,
        0x0000000000007fffULL, 0x000000000000ffffULL, 0x000000000001ffffULL,
        0x000000000003ffffULL, 0x000000000007ffffULL, 0x00000000000fffffULL,
        0x00000000001fffffULL, 0x00000000003fffffULL, 0x00000000007fffffULL,
        0x0000000000ffffffULL, 0x0000000001ffffffULL, 0x0000000003ffffffULL,
        0x0000000007ffffffULL, 0x000000000fffffffULL, 0x000000001fffffffULL,
        0x000000003fffffffULL, 0x000000007fffffffULL, 0x00000000ffffffffULL,
        0x00000001ffffffffULL, 0x00000003ffffffffULL, 0x00000007ffffffffULL,
        0x0000000fffffffffULL, 0x0000001fffffffffULL, 0x0000003fffffffffULL,
        0x0000007fffffffffULL, 0x000000ffffffffffULL, 0x000001ffffffffffULL,
        0x000003ffffffffffULL, 0x000007ffffffffffULL, 0x00000fffffffffffULL,
        0x00001fffffffffffULL, 0x00003fffffffffffULL, 0x00007fffffffffffULL,
        0x0000ffffffffffffULL, 0x0001ffffffffffffULL, 0x0003ffffffffffffULL,
        0x0007ffffffffffffULL, 0x000fffffffffffffULL, 0x001fffffffffffffULL,
        0x003fffffffffffffULL, 0x007fffffffffffffULL, 0x00ffffffffffffffULL,
        0x01ffffffffffffffULL, 0x03ffffffffffffffULL, 0x07ffffffffffffffULL,
        0x0fffffffffffffffULL, 0x1fffffffffffffffULL, 0x3fffffffffffffffULL,
        0x7fffffffffffffffULL, 0xffffffffffffffffULL};

    if (length < (sizeof(bitmask_table) / sizeof(bitmask_table[0])))
        return bitmask_table[length];
    else
        return 0xffffffffffffffffULL;
}

/** @fn uint64_t apply_linear_uint64_t(uint64_t bitfield, double scale, double
 * offset)
 *  @brief apply a linear conversion to a 64 bit unsigned number.
 *  @param bitfield 64 bit unsigned data
 *  @param scale Scaling to apply
 *  @param offset Offset to apply
 */
uint64_t apply_linear_uint64_t(uint64_t bitfield, double scale, double offset) {
    if (scale == 1.0) {
        return bitfield + (uint64_t)offset;
    } else {
        return scale * (uint32_t)bitfield + offset;
    }
}

/** @fn int64_t apply_linear_int64_t(int64_t bitfield, double scale, double
 * offset)
 *  @brief apply a linear conversion to a 64 bit signed number. Only applies
 *  transformations for numbers up to 32 bit
 *  @param bitfield 64 bit signed data.
 *  @param scale Scaling to apply.
 *  @param offset Offset to apply.
 */
int64_t apply_linear_int64_t(int64_t bitfield, double scale, double offset) {
    if (scale == 1.0) {
        return bitfield + (int64_t)offset;
    }

    else {
        return scale * (int32_t)bitfield + offset;
    }
}

/** @fn double apply_linear_double(double bitfield, double scale, double offset)
 *  @brief apply a linear conversion to a double.
 *  @param bitfield double.
 *  @param scale Scaling to apply.
 *  @param offset Offset to apply.
 */
double apply_linear_double(double bitfield, double scale, double offset) {
    return scale * bitfield + offset;
}

/** @fn float apply_linear_float(float bitfield, double scale, double offset)
 *  @brief apply a linear conversion to a float.
 *  @param bitfield float.
 *  @param scale Scaling to apply.
 *  @param offset Offset to apply.
 */
float apply_linear_float(float bitfield, double scale, double offset) {
    return scale * bitfield + offset;
}

/** @fn int64_t bitfield_sign_conv(uint64_t bitfield, unsigned length)
 *  @brief change sign of a 64 bit signed number
 *  @param bitfield The number.
 *  @param length Size of the number
 */
int64_t bitfield_sign_conv(uint64_t bitfield, unsigned length) {
    if (get_bit(bitfield, (length - 1))) {
        return (int64_t)((0xFFFFFFFFFFFFFFFFUL << length) | (bitfield));
    } else {
        return (int64_t)bitfield;
    }
}

uint64_t can_can_decode_signal_as_uint64_t(const CanFrame *msg, uint64_t start,
                                           uint64_t length, double scale,
                                           double offset) {
    uint64_t bitfield = get_bitfield(can_word(msg), start, length);
    return apply_linear_uint64_t(bitfield, scale, offset);
}

uint64_t can_encode_signal_from_uint64_t(uint64_t signal, uint64_t start,
                                         uint64_t length, double scale,
                                         double offset) {
    return set_bitfield(apply_linear_uint64_t(signal, 1 / scale, -offset),
                        start, length);
}

uint32_t can_decode_signal_as_uint32_t(const CanFrame *msg, uint64_t start,
                                       uint64_t length, double scale,
                                       double offset) {
    uint64_t bitfield = get_bitfield(can_word(msg), start, length);
    return apply_linear_uint64_t(bitfield, scale, offset);
}

uint64_t can_encode_signal_from_uint32_t(uint32_t signal, uint64_t start,
                                         uint64_t length, double scale,
                                         double offset) {
    return set_bitfield(apply_linear_uint64_t(signal, 1 / scale, -offset),
                        start, length);
}

uint16_t can_decode_signal_as_uint16_t(const CanFrame *msg, uint64_t start,
                                       uint64_t length, double scale,
                                       double offset) {
    uint64_t bitfield = get_bitfield(can_word(msg), start, length);
    return apply_linear_uint64_t(bitfield, scale, offset);
}

uint64_t can_encode_signal_from_uint16_t(uint16_t signal, uint64_t start,
                                         uint64_t length, double scale,
                                         double offset) {
    return set_bitfield(apply_linear_uint64_t(signal, 1 / scale, -offset),
                        start, length);
}

uint8_t can_decode_signal_as_uint8_t(const CanFrame *msg, uint64_t start,
                                     uint64_t length, double scale,
                                     double offset) {
    uint64_t bitfield = get_bitfield(can_word(msg), start, length);
    return apply_linear_uint64_t(bitfield, scale, offset);
}

uint64_t can_encode_signal_from_uint8_t(uint8_t signal, uint64_t start,
                                        uint64_t length, double scale,
                                        double offset) {
    return set_bitfield(apply_linear_uint64_t(signal, 1 / scale, -offset),
                        start, length);
}

/* Only works up to 32 bit */
double can_decode_signal_as_double(const CanFrame *msg, uint64_t start,
                                   uint64_t length, double scale,
                                   double offset) {
    uint64_t bitfield = get_bitfield(can_word(msg), start, length);
    return apply_linear_double(bitfield, scale, offset);
}

uint64_t can_encode_signal_from_double(double signal, uint64_t start,
                                       uint64_t length, double scale,
                                       double offset) {
    return set_bitfield(apply_linear_double(signal, 1 / scale, -offset), start,
                        length);
}

/* Only works up to 32 bit */
float can_decode_signal_as_float(const CanFrame *msg, uint64_t start,
                                 uint64_t length, double scale, double offset) {
    uint64_t bitfield = get_bitfield(can_word(msg), start, length);
    return apply_linear_double(bitfield, scale, offset);
}

uint64_t can_encode_signal_from_float(float signal, uint64_t start,
                                      uint64_t length, double scale,
                                      double offset) {
    return set_bitfield(apply_linear_double(signal, 1 / scale, -offset), start,
                        length);
}

int64_t can_decode_signal_as_int64_t(const CanFrame *msg, uint64_t start,
                                     uint64_t length, double scale,
                                     double offset) {

    int64_t bitfield =
        bitfield_sign_conv(get_bitfield(can_word(msg), start, length), length);

    return apply_linear_int64_t(bitfield, scale, offset);
}

uint64_t can_encode_signal_from_int64_t(int64_t signal, uint64_t start,
                                        uint64_t length, double scale,
                                        double offset) {
    return set_bitfield(apply_linear_int64_t(signal, 1 / scale, -offset), start,
                        length);
}

int32_t can_decode_signal_as_int32_t(const CanFrame *msg, uint64_t start,
                                     uint64_t length, double scale,
                                     double offset) {

    int64_t bitfield =
        bitfield_sign_conv(get_bitfield(can_word(msg), start, length), length);

    return apply_linear_int64_t(bitfield, scale, offset);
}

uint64_t can_encode_signal_from_int32_t(int32_t signal, uint64_t start,
                                        uint64_t length, double scale,
                                        double offset) {
    return set_bitfield(apply_linear_int64_t(signal, 1 / scale, -offset), start,
                        length);
}

int16_t can_decode_signal_as_int16_t(const CanFrame *msg, uint64_t start,
                                     uint64_t length, double scale,
                                     double offset) {

    int64_t bitfield =
        bitfield_sign_conv(get_bitfield(can_word(msg), start, length), length);

    return apply_linear_int64_t(bitfield, scale, offset);
}

uint64_t can_encode_signal_from_int16_t(int16_t signal, uint64_t start,
                                        uint64_t length, double scale,
                                        double offset) {
    return set_bitfield(apply_linear_int64_t(signal, 1 / scale, -offset), start,
                        length);
}

int8_t can_decode_signal_as_int8_t(const CanFrame *msg, uint64_t start,
                                   uint64_t length, double scale,
                                   double offset) {

    int64_t bitfield =
        bitfield_sign_conv(get_bitfield(can_word(msg), start, length), length);

    return apply_linear_int64_t(bitfield, scale, offset);
}

uint64_t can_encode_signal_from_int8_t(int8_t signal, uint64_t start,
                                       uint64_t length, double scale,
                                       double offset) {
    return set_bitfield(apply_linear_int64_t(signal, 1 / scale, -offset), start,
                        length);
}

float can_decode_signal_float_as_float(const CanFrame *msg, uint64_t start,
                                       uint64_t length, double scale,
                                       double offset) {
    if (length != 32) {
        return 0.0;
    }

    uint64_t word = get_bitfield(can_word(msg), start, length);
    float f = *((float *)&word);
    return apply_linear_float(f, scale, offset);
}

uint64_t can_encode_signal_float_from_float(float signal, uint64_t start,
                                            uint64_t length, double scale,
                                            double offset) {
    float d = apply_linear_double(signal, 1 / scale, -offset);
    uint32_t word = *(uint32_t *)&d;
    return set_bitfield(word, start, length);
}

double can_decode_signal_double_as_double(const CanFrame *msg, uint64_t start,
                                          uint64_t length, double scale,
                                          double offset) {
    if (length != 64) {
        return 0.0;
    }

    uint64_t word = get_bitfield(can_word(msg), start, length);
    double f = *((double *)&word);
    return apply_linear_double(f, scale, offset);
}

uint64_t can_encode_signal_double_from_double(double signal, uint64_t start,
                                              uint64_t length, double scale,
                                              double offset) {
    double d = apply_linear_double(signal, 1 / scale, -offset);
    uint64_t word = *(uint64_t *)&d;
    return set_bitfield(word, start, length);
}
#ifdef __cplusplus
}
#endif
