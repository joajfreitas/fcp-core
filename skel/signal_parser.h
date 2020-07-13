#ifndef __SIGNAL_PARSER_H__
#define __SIGNAL_PARSER_H__

#include <stdint.h>

#include "candata.h"

typedef enum _fcp_endianess {
	LITTLE,
	BIG
} fcp_endianess_t;

typedef enum _fcp_type {
	UNSIGNED,
	SIGNED,
	FLOAT,
	DOUBLE
} fcp_type_t;

typedef struct _signal {
	uint16_t start;
	uint16_t length;
	double scale;
	double offset;
	fcp_type_t type;
	fcp_endianess_t endianess;
} fcp_signal_t;

uint64_t bitmask(unsigned length);

uint64_t fcp_decode_signal_uint64_t(CANdata msg, fcp_signal_t signal);
uint32_t fcp_decode_signal_uint32_t(CANdata msg, fcp_signal_t signal);
uint16_t fcp_decode_signal_uint16_t(CANdata msg, fcp_signal_t signal);
uint8_t fcp_decode_signal_uint8_t(CANdata msg, fcp_signal_t signal);
int64_t fcp_decode_signal_int64_t(CANdata msg, fcp_signal_t signal);
int32_t fcp_decode_signal_int32_t(CANdata msg, fcp_signal_t signal);
int16_t fcp_decode_signal_int16_t(CANdata msg, fcp_signal_t signal);
int8_t fcp_decode_signal_int8_t(CANdata msg, fcp_signal_t signal);
double fcp_decode_signal_double(CANdata msg, fcp_signal_t signal);
float fcp_decode_signal_float(CANdata msg, fcp_signal_t signal);

uint64_t fcp_encode_signal_uint64_t(uint64_t value, fcp_signal_t);
uint64_t fcp_encode_signal_uint32_t(uint32_t value, fcp_signal_t);
uint64_t fcp_encode_signal_uint16_t(uint16_t value, fcp_signal_t);
uint64_t fcp_encode_signal_uint8_t(uint8_t value, fcp_signal_t);
uint64_t fcp_encode_signal_int64_t(int64_t value, fcp_signal_t);
uint64_t fcp_encode_signal_int32_t(int32_t value, fcp_signal_t);
uint64_t fcp_encode_signal_int16_t(int16_t value, fcp_signal_t);
uint64_t fcp_encode_signal_int8_t(int8_t value, fcp_signal_t);
uint64_t fcp_encode_signal_double(double value, fcp_signal_t);
uint64_t fcp_encode_signal_float(float value, fcp_signal_t);

#endif /* ifndef __SIGNAL_PARSER_H__ */
