#ifndef CAN_FRAME_H
#define CAN_FRAME_H

#include <stdint.h>

typedef struct _can_frame {
    uint8_t ide : 1;
    uint16_t sid : 11;
    uint32_t eid : 18;
    uint8_t dlc : 4;
    uint8_t data[8] __attribute__((aligned(2)));
} CANFrame;

typedef struct _can_frame CAN2BFrame;
typedef struct _can_frame CANdata;

#endif
