#ifndef ECU_CAN_H
#define ECU_CAN_H

#include <stdint.h>
#include <stdbool.h>

#include "can_frame.h"

/* Ecu Message IDs */
#define MSG_ID_PEDALS 10
#define MSG_ID_SHUTDOWN 11

/* Ecu Message Periods */
#define MSG_PERIOD_PEDALS 15
#define MSG_PERIOD_SHUTDOWN 30

typedef struct {
    uint8_t acc_pos;
    uint8_t brake_pos;
} CanMsgPedals;

typedef struct {
    uint8_t error;
} CanMsgShutdown;

/* Ecu device struct. Contains one instance of each device message */
typedef struct {
    CanMsgPedals pedals;
    CanMsgShutdown shutdown;
} CanDeviceEcu;


/* Check if a CanFrame comes from Ecu */
bool can_is_ecu_msg(const CanFrame *frame);

/* Send Ecu messages according to period */
void can_send_ecu_msgs_scheduled(const CanDeviceEcu *dev, uint32_t time, void (*send_can_func)(const CanFrame *));

/* Functions to decode CanFrame into CanMsg<name> objects */
CanMsgPedals can_decode_msg_pedals(const CanFrame *frame);
CanMsgShutdown can_decode_msg_shutdown(const CanFrame *frame);

/* Functions to encode CanMsg<name> object into CanFrame */
CanFrame can_encode_msg_pedals(const CanMsgPedals *msg);
CanFrame can_encode_msg_shutdown(const CanMsgShutdown *msg);

#endif // ECU_CAN_H