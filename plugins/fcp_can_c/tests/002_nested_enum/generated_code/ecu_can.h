#ifndef ECU_CAN_H
#define ECU_CAN_H

#include <stdint.h>
#include <stdbool.h>

#include "can_frame.h"
#include "global_can.h"

/* Ecu Message IDs */
#define CAN_MSG_ID_FOO 11

/* Ecu Message Periods */
#define CAN_MSG_PERIOD_FOO 0

typedef struct {
    uint8_t s1;
    uint16_t s2;
    MyEnum s3;
} CanMsgFoo;

/* Ecu device struct. Contains one instance of each device message */
typedef struct {
    CanMsgFoo foo;
} CanDeviceEcu;


/* Check if a CanFrame comes from Ecu */
bool can_is_ecu_msg(const CanFrame *frame);


/* Send Ecu messages according to period */
void can_send_ecu_msgs_scheduled(const CanDeviceEcu *dev, uint32_t time, void (*send_can_func)(const CanFrame *));


/* Functions to decode CanFrame into CanMsg<name> objects */
CanMsgFoo can_decode_msg_foo(const CanFrame *frame);

/* Functions to encode CanMsg<name> object into CanFrame */
CanFrame can_encode_msg_foo(const CanMsgFoo *msg);

#endif // ECU_CAN_H