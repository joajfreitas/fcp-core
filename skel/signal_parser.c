#include <stdio.h>

#include "signal_parser.h"
#include "candata.h"



/* Taken from glib source */

/* Swap bytes in 16-bit value.  */
#define __bswap_16(x)                                        \
  ((uint16_t) ((((x) >> 8) & 0xff) | (((x) & 0xff) << 8)))

/* Swap bytes in 32-bit value.  */
#define __bswap_32(x)                                        \
  ((((x) & 0xff000000u) >> 24) | (((x) & 0x00ff0000u) >> 8)        \
   | (((x) & 0x0000ff00u) << 8) | (((x) & 0x000000ffu) << 24))

/* Swap bytes in 64-bit value.  */
#define __bswap_64(x)                        \
  ((((x) & 0xff00000000000000ull) >> 56)        \
   | (((x) & 0x00ff000000000000ull) >> 40)        \
   | (((x) & 0x0000ff0000000000ull) >> 24)        \
   | (((x) & 0x000000ff00000000ull) >> 8)        \
   | (((x) & 0x00000000ff000000ull) << 8)        \
   | (((x) & 0x0000000000ff0000ull) << 24)        \
   | (((x) & 0x000000000000ff00ull) << 40)        \
   | (((x) & 0x00000000000000ffull) << 56))



/** @def get_bit(word, pos) (word >> pos) & 0x1
 * Get a bit from a bitfield
 */
#define get_bit(word, pos) (word >> pos) & 0x1

/** @def can_word(msg) (*((uint64_t *) (msg.data)))
 *  Convert CANdata to uint64_t word with data contents.
 */
#define can_word(msg) (*((uint64_t *) (msg.data)))

#define cast_double(ptr) *((double *) (ptr))
#define cast_float(ptr) *((float *) (ptr))
#define get_bitfield(data, signal) (((data) >> (signal.start)) & bitmask(signal.length))
#define set_bitfield(data, signal) (((uint64_t) data) << signal.start)

uint64_t apply_linear_uint64_t(uint64_t bitfield, fcp_signal_t signal);
int64_t apply_linear_int64_t(int64_t bitfield, fcp_signal_t signal);
double apply_linear_double(double bitfield, fcp_signal_t signal);
float apply_linear_float(float bitfield, fcp_signal_t signal);
int64_t bitfield_sign_conv(uint64_t bitfield, fcp_signal_t signal);



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
		0x7fffffffffffffffULL, 0xffffffffffffffffULL 
	};

	if (length < (sizeof(bitmask_table) / sizeof(bitmask_table[0]))) {
        return bitmask_table[length];
	}
    else
        return 0xffffffffffffffffULL;
}

/** @fn uint64_t apply_linear_uint64_t(uint64_t bitfield, double scale, double offset)
 *  @brief apply a linear conversion to a 64 bit unsigned number.
 *  @param bitfield 64 bit unsigned data
 *  @param scale Scaling to apply
 *  @param offset Offset to apply
 */
uint64_t apply_linear_uint64_t(uint64_t bitfield, fcp_signal_t signal) {
	if (signal.scale == 1.0) {
		return bitfield + (uint64_t) signal.offset;
	}
	else {
		return signal.scale*(uint32_t)bitfield+signal.offset;
	}
}


/** @fn int64_t apply_linear_int64_t(int64_t bitfield, double scale, double offset)
 *  @brief apply a linear conversion to a 64 bit signed number. Only applies
 *  transformations for numbers up to 32 bit
 *  @param bitfield 64 bit signed data.
 *  @param scale Scaling to apply.
 *  @param offset Offset to apply.
 */
int64_t apply_linear_int64_t(int64_t bitfield, fcp_signal_t signal){
	if (signal.scale == 1.0) {
		return bitfield + (int64_t) signal.offset;
	}

	else {
		return signal.scale*(int32_t)bitfield+signal.offset;
	}
}

/** @fn double apply_linear_double(double bitfield, double scale, double offset)
 *  @brief apply a linear conversion to a double.
 *  @param bitfield double.
 *  @param scale Scaling to apply.
 *  @param offset Offset to apply.
 */
double apply_linear_double(double bitfield, fcp_signal_t signal) {
	return signal.scale*bitfield+signal.offset;
}

/** @fn float apply_linear_float(float bitfield, double scale, double offset)
 *  @brief apply a linear conversion to a float.
 *  @param bitfield float.
 *  @param scale Scaling to apply.
 *  @param offset Offset to apply.
 */
float apply_linear_float(float bitfield, fcp_signal_t signal) {
	return signal.scale*bitfield+signal.offset;
}

/** @fn int64_t bitfield_sign_conv(uint64_t bitfield, unsigned length) 
 *  @brief change sign of a 64 bit signed number
 *  @param bitfield The number.
 *  @param length Size of the number
 */
int64_t bitfield_sign_conv(uint64_t bitfield, fcp_signal_t signal) {
	if (get_bit(bitfield, (signal.length-1))) {
		return (int64_t) ((0xFFFFFFFFFFFFFFFFUL << signal.length) | (bitfield));
	}
	else {
		return (int64_t) bitfield;
	}
}

uint64_t big_endian_conv(uint64_t word, fcp_signal_t signal);
uint64_t big_endian_conv(uint64_t word, fcp_signal_t signal) {
	if (signal.endianess != BIG) {
		return word;
	}
	
	switch (signal.length) {
	case 16:
		return (uint64_t) __bswap_16((uint16_t) word);
	case 32:
		return (uint64_t) __bswap_32((uint32_t) word);
	case 64:
		return (uint64_t) __bswap_64((uint64_t) word);
	default:
		return word;
	}
}

#define decode_signal(_type) \
_type fcp_decode_signal_ ## _type (CANdata msg, fcp_signal_t signal) { \
	switch (signal.type) { \
	case UNSIGNED: \
		return (_type) apply_linear_uint64_t(  \
				big_endian_conv( \
					get_bitfield(can_word(msg), signal), signal), signal); \
	case SIGNED: \
		return (_type) apply_linear_int64_t( \
				bitfield_sign_conv( \
					big_endian_conv( \
						get_bitfield(can_word(msg), signal), signal), signal), signal);	 \
	case FLOAT: \
		return (_type) apply_linear_double( \
				big_endian_conv( \
					get_bitfield(can_word(msg), signal), signal), signal); \
	case DOUBLE: \
		return (_type) apply_linear_double( \
				bitfield_sign_conv( \
					big_endian_conv( \
						get_bitfield(can_word(msg), signal), signal), signal), signal); \
	default: \
		return 0; \
	} \
}

// clang format off
decode_signal(uint64_t)
decode_signal(uint32_t)
decode_signal(uint16_t)
decode_signal(uint8_t)
decode_signal(int64_t)
decode_signal(int32_t)
decode_signal(int16_t)
decode_signal(int8_t)
decode_signal(float)
decode_signal(double)
// clang format on


#define encode_signal(_type) \
uint64_t fcp_encode_signal_ ## _type ( _type value, fcp_signal_t signal) { \
	signal.scale = 1/signal.scale; \
	signal.offset = -signal.offset; \
	uint64_t word = 0; \
	double d32 = 0, d64 = 0; \
	switch (signal.type) { \
	case UNSIGNED: \
		return set_bitfield( \
				big_endian_conv( \
				apply_linear_uint64_t( (uint64_t) value, signal), signal), signal); \
	case SIGNED: \
		return set_bitfield( \
				big_endian_conv( (uint64_t) \
				apply_linear_int64_t((int64_t) value, signal), signal), signal); \
	case FLOAT: \
		d32 = apply_linear_double(value, signal); \
		word = *(uint32_t *) &d32; \
		return set_bitfield(big_endian_conv(word, signal), signal); \
	case DOUBLE: \
		d64 = apply_linear_double(value, signal); \
		word = *(uint64_t *) &d64; \
		return set_bitfield(big_endian_conv(word, signal), signal); \
	default: \
		return 0; \
	} \
	return 0; \
}\

// clang-format off
encode_signal(uint64_t)
encode_signal(uint32_t)
encode_signal(uint16_t)
encode_signal(uint8_t)
encode_signal(int64_t)
encode_signal(int32_t)
encode_signal(int16_t)
encode_signal(int8_t)
encode_signal(float)
encode_signal(double)
// clang-format on
