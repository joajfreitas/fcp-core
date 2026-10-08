#ifndef CAN_FRAME_H
#define CAN_FRAME_H

#include <stdint.h>

typedef struct {
    uint8_t ide : 1;
    uint16_t id : 11;
    uint32_t eid : 18;
    uint8_t dlc : 4;
    uint8_t data[8];
} CanFrame;

#endif
