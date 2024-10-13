#ifndef CAN_SIGNAL_PARSER_H
#define CAN_SIGNAL_PARSER_H

#include <stdint.h>

#include "can_frame.h"

#ifdef __cplusplus
extern "C" {
#endif

uint64_t can_decode_signal_unsigned_as_uint64_t(CanFrame msg, uint64_t start,
                                                uint64_t length, double scale,
                                                double offset);

uint64_t can_encode_signal_unsigned_from_uint64_t(uint64_t signal,
                                                  uint64_t start,
                                                  uint64_t length, double scale,
                                                  double offset);

uint32_t can_decode_signal_unsigned_as_uint32_t(CanFrame msg, uint64_t start,
                                                uint64_t length, double scale,
                                                double offset);

uint64_t can_encode_signal_unsigned_from_uint32_t(uint32_t signal,
                                                  uint64_t start,
                                                  uint64_t length, double scale,
                                                  double offset);

uint16_t can_decode_signal_unsigned_as_uint16_t(CanFrame msg, uint64_t start,
                                                uint64_t length, double scale,
                                                double offset);

uint64_t can_encode_signal_unsigned_from_uint16_t(uint16_t signal,
                                                  uint64_t start,
                                                  uint64_t length, double scale,
                                                  double offset);

uint8_t can_decode_signal_unsigned_as_uint8_t(CanFrame msg, uint64_t start,
                                              uint64_t length, double scale,
                                              double offset);

uint64_t can_encode_signal_unsigned_from_uint8_t(uint8_t signal, uint64_t start,
                                                 uint64_t length, double scale,
                                                 double offset);

double can_decode_signal_unsigned_as_double(CanFrame msg, uint64_t start,
                                            uint64_t length, double scale,
                                            double offset);

uint64_t can_encode_signal_unsigned_from_double(double signal, uint64_t start,
                                                uint64_t length, double scale,
                                                double offset);

float can_decode_signal_unsigned_as_float(CanFrame msg, uint64_t start,
                                          uint64_t length, double scale,
                                          double offset);

uint64_t can_encode_signal_unsigned_from_float(float signal, uint64_t start,
                                               uint64_t length, double scale,
                                               double offset);

int64_t can_decode_signal_signed_as_int64_t(CanFrame msg, uint64_t start,
                                            uint64_t length, double scale,
                                            double offset);

uint64_t can_encode_signal_signed_from_int64_t(int64_t signal, uint64_t start,
                                               uint64_t length, double scale,
                                               double offset);

int32_t can_decode_signal_signed_as_int32_t(CanFrame msg, uint64_t start,
                                            uint64_t length, double scale,
                                            double offset);

uint64_t can_encode_signal_signed_from_int32_t(int32_t signal, uint64_t start,
                                               uint64_t length, double scale,
                                               double offset);

int16_t can_decode_signal_signed_as_int16_t(CanFrame msg, uint64_t start,
                                            uint64_t length, double scale,
                                            double offset);

uint64_t can_encode_signal_signed_from_int16_t(int16_t signal, uint64_t start,
                                               uint64_t length, double scale,
                                               double offset);

int8_t can_decode_signal_signed_as_int8_t(CanFrame msg, uint64_t start,
                                          uint64_t length, double scale,
                                          double offset);

uint64_t can_encode_signal_signed_from_int8_t(int8_t signal, uint64_t start,
                                              uint64_t length, double scale,
                                              double offset);

double can_decode_signal_signed_as_double(CanFrame msg, uint64_t start,
                                          uint64_t length, double scale,
                                          double offset);

uint64_t can_encode_signal_signed_from_double(double signal, uint64_t start,
                                              uint64_t length, double scale,
                                              double offset);

float can_decode_signal_signed_as_float(CanFrame msg, uint64_t start,
                                        uint64_t length, double scale,
                                        double offset);

uint64_t can_encode_signal_signed_from_float(float signal, uint64_t start,
                                             uint64_t length, double scale,
                                             double offset);

float can_decode_signal_float_as_float(CanFrame msg, uint64_t start,
                                       uint64_t length, double scale,
                                       double offset);

uint64_t can_encode_signal_float_from_float(float signal, uint64_t start,
                                            uint64_t length, double scale,
                                            double offset);

double can_decode_signal_double_as_double(CanFrame msg, uint64_t start,
                                          uint64_t length, double scale,
                                          double offset);

uint64_t can_encode_signal_double_from_double(double signal, uint64_t start,
                                              uint64_t length, double scale,
                                              double offset);

uint64_t bitmask(unsigned lenght);
#ifdef __cplusplus
}
#endif
#endif /* ifndef __SIGNAL_PARSER_H__ */
