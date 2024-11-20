#ifndef CAN_SIGNAL_PARSER_H
#define CAN_SIGNAL_PARSER_H

#include <stdbool.h>
#include <stdint.h>

#include "can_frame.h"

#ifdef __cplusplus
extern "C" {
#endif

uint64_t can_decode_signal_as_uint64_t(const CanFrame *msg, uint32_t start, uint32_t length,
                                       float scale, float offset, bool is_big_endian);

uint64_t can_encode_signal_from_uint64_t(uint64_t signal, uint32_t start, uint32_t length,
                                         float scale, float offset, bool is_big_endian);

uint32_t can_decode_signal_as_uint32_t(const CanFrame *msg, uint32_t start, uint32_t length,
                                       float scale, float offset, bool is_big_endian);

uint64_t can_encode_signal_from_uint32_t(uint32_t signal, uint32_t start, uint32_t length,
                                         float scale, float offset, bool is_big_endian);

uint16_t can_decode_signal_as_uint16_t(const CanFrame *msg, uint32_t start, uint32_t length,
                                       float scale, float offset, bool is_big_endian);

uint64_t can_encode_signal_from_uint16_t(uint16_t signal, uint32_t start, uint32_t length,
                                         float scale, float offset, bool is_big_endian);

uint8_t can_decode_signal_as_uint8_t(const CanFrame *msg, uint32_t start, uint32_t length,
                                     float scale, float offset, bool is_big_endian);

uint64_t can_encode_signal_from_uint8_t(uint8_t signal, uint32_t start, uint32_t length,
                                        float scale, float offset, bool is_big_endian);

double can_decode_signal_as_double(const CanFrame *msg, uint32_t start, uint32_t length,
                                   float scale, float offset, bool is_big_endian);

uint64_t can_encode_signal_from_double(double signal, uint32_t start, uint32_t length, float scale,
                                       float offset, bool is_big_endian);

float can_decode_signal_as_float(const CanFrame *msg, uint32_t start, uint32_t length, float scale,
                                 float offset, bool is_big_endian);

uint64_t can_encode_signal_from_float(float signal, uint32_t start, uint32_t length, float scale,
                                      float offset, bool is_big_endian);

int64_t can_decode_signal_as_int64_t(const CanFrame *msg, uint32_t start, uint32_t length,
                                     float scale, float offset, bool is_big_endian);

uint64_t can_encode_signal_from_int64_t(int64_t signal, uint32_t start, uint32_t length,
                                        float scale, float offset, bool is_big_endian);

int32_t can_decode_signal_as_int32_t(const CanFrame *msg, uint32_t start, uint32_t length,
                                     float scale, float offset, bool is_big_endian);

uint64_t can_encode_signal_from_int32_t(int32_t signal, uint32_t start, uint32_t length,
                                        float scale, float offset, bool is_big_endian);

int16_t can_decode_signal_as_int16_t(const CanFrame *msg, uint32_t start, uint32_t length,
                                     float scale, float offset, bool is_big_endian);

uint64_t can_encode_signal_from_int16_t(int16_t signal, uint32_t start, uint32_t length,
                                        float scale, float offset, bool is_big_endian);

int8_t can_decode_signal_as_int8_t(const CanFrame *msg, uint32_t start, uint32_t length,
                                   float scale, float offset, bool is_big_endian);

uint64_t can_encode_signal_from_int8_t(int8_t signal, uint32_t start, uint32_t length, float scale,
                                       float offset, bool is_big_endian);

double can_decode_signal_as_double(const CanFrame *msg, uint32_t start, uint32_t length,
                                   float scale, float offset, bool is_big_endian);

uint64_t can_encode_signal_from_double(double signal, uint32_t start, uint32_t length, float scale,
                                       float offset, bool is_big_endian);

float can_decode_signal_as_float(const CanFrame *msg, uint32_t start, uint32_t length, float scale,
                                 float offset, bool is_big_endian);

uint64_t can_encode_signal_from_float(float signal, uint32_t start, uint32_t length, float scale,
                                      float offset, bool is_big_endian);

float can_decode_signal_float_as_float(const CanFrame *msg, uint32_t start, uint32_t length,
                                       float scale, float offset, bool is_big_endian);

uint64_t can_encode_signal_float_from_float(float signal, uint32_t start, uint32_t length,
                                            float scale, float offset, bool is_big_endian);

double can_decode_signal_double_as_double(const CanFrame *msg, uint32_t start, uint32_t length,
                                          float scale, float offset, bool is_big_endian);

uint64_t can_encode_signal_double_from_double(double signal, uint32_t start, uint32_t length,
                                              float scale, float offset, bool is_big_endian);

uint64_t bitmask(unsigned length);
#ifdef __cplusplus
}
#endif
#endif /* ifndef __SIGNAL_PARSER_H__ */
