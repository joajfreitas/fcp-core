#include <stdio.h>

#include "signal_parser.h"
#include "candata.h"

// token to string
#define STRINGIFY(x) #x
#define TOSTRING(x) STRINGIFY(x)
#define AT __FILE__ ":" TOSTRING(__LINE__)

// define a function for every tipe
#define fcp_type_generic(function) \
function(uint64_t) \
function(uint32_t) \
function(uint16_t) \
function(uint8_t) \
function(int64_t) \
function(int32_t) \
function(int16_t) \
function(int8_t) \
function(float) \
function(double) \


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

//uint64_t apply_linear_uint64_t(uint64_t bitfield, fcp_signal_t signal);
//int64_t apply_linear_int64_t(int64_t bitfield, fcp_signal_t signal);
//double apply_linear_double(double bitfield, fcp_signal_t signal);
//float apply_linear_float(float bitfield, fcp_signal_t signal);
//int64_t bitfield_sign_conv(uint64_t bitfield, fcp_signal_t signal);



/** @fn uint64_t bitmask(unsigned length) 
 *  @brief Generate a bitmask with length bits set to 1.
 *  @param length Size of the bit mask
 */
uint64_t bitmask(unsigned length) {
	if (length >= 64) {
		return 0xffffffffffffffffULL;
	}
	else {
		return (1ULL << length) - 1;
	}
	
}

#define apply_linear(type) \
type apply_linear_ ## type (type bitfield, fcp_signal_t signal); \
type apply_linear_ ## type ( type bitfield, fcp_signal_t signal) { \
	if (signal.scale == 1.0) { \
		return (type) (bitfield + (type) signal.offset); \
	} \
	else { \
		/*printf("apply_linear_" STRINGIFY(type)": %lld \n", (unsigned long long) bitfield); */\
		return (type) (signal.scale * ((double) bitfield) + signal.offset);\
	}\
}

fcp_type_generic(apply_linear)
	
/** @fn int64_t bitfield_sign_conv(uint64_t bitfield, unsigned length) 
 *  @brief change sign of a 64 bit signed number
 *  @param bitfield The number.
 *  @param length Size of the number
 */
int64_t bitfield_sign_conv(uint64_t bitfield, fcp_signal_t signal);
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

// clang format off
#define decode_signal(_type) \
_type fcp_decode_signal_ ## _type (CANdata msg, fcp_signal_t signal) { \
	switch (signal.type) { \
	case UNSIGNED: \
		return (_type) apply_linear_ ## _type (  \
				big_endian_conv( (uint64_t) \
					get_bitfield(can_word(msg), signal), signal), signal); \
	case SIGNED: \
		return (_type) apply_linear_ ## _type( \
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

fcp_type_generic(decode_signal)


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

fcp_type_generic(encode_signal)
// clang-format on
