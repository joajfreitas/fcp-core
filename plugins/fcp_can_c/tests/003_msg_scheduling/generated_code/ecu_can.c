#include "ecu_can.h"
#include "can_signal_parser.h"

/*-------------------- Decode Signals ---------------------*/
// Pedals
#define can_decode_signal_pedals_acc_pos(msg) \
    can_decode_signal_as_uint8_t((msg), 0, 8, 1.0, 0.0)
#define can_decode_signal_pedals_brake_pos(msg) \
    can_decode_signal_as_uint8_t((msg), 8, 8, 1.0, 0.0)
// Shutdown
#define can_decode_signal_shutdown_error(msg) \
    can_decode_signal_as_uint8_t((msg), 0, 8, 1.0, 0.0)
// Button
#define can_decode_signal_button_press(msg) \
    can_decode_signal_as_uint8_t((msg), 0, 8, 1.0, 0.0)
/*---------------------------------------------------------*/

/*-------------------- Encode Signals ---------------------*/
// Pedals
#define can_encode_signal_pedals_acc_pos(signal) \
    can_encode_signal_from_uint8_t((signal), 0, 8, 1.0, 0.0);
#define can_encode_signal_pedals_brake_pos(signal) \
    can_encode_signal_from_uint8_t((signal), 8, 8, 1.0, 0.0);
// Shutdown
#define can_encode_signal_shutdown_error(signal) \
    can_encode_signal_from_uint8_t((signal), 0, 8, 1.0, 0.0);
// Button
#define can_encode_signal_button_press(signal) \
    can_encode_signal_from_uint8_t((signal), 0, 8, 1.0, 0.0);
/*---------------------------------------------------------*/

bool can_is_ecu_msg(const CanFrame *frame) {
    return
        frame->id == CAN_MSG_ID_PEDALS ||
        frame->id == CAN_MSG_ID_SHUTDOWN ||
        frame->id == CAN_MSG_ID_BUTTON;
}


void can_send_ecu_msgs_scheduled(const CanDeviceEcu *dev, uint32_t time, void (*send_can_func)(const CanFrame *)) {
    static uint32_t last_call_t = 0;
    static uint32_t last_send_t[3] = {0};

    if (last_call_t == time) return;
    last_call_t = time;

    // Check if enough time has passed for Pedals
    if (CAN_MSG_PERIOD_PEDALS != -1 && (time - last_send_t[0] >= CAN_MSG_PERIOD_PEDALS)) {
        CanFrame frame = can_encode_msg_pedals(&dev->pedals);
        send_can_func(&frame);
        last_send_t[0] = time;
    }
    // Check if enough time has passed for Shutdown
    if (CAN_MSG_PERIOD_SHUTDOWN != -1 && (time - last_send_t[1] >= CAN_MSG_PERIOD_SHUTDOWN)) {
        CanFrame frame = can_encode_msg_shutdown(&dev->shutdown);
        send_can_func(&frame);
        last_send_t[1] = time;
    }
    // Check if enough time has passed for Button
    if (CAN_MSG_PERIOD_BUTTON != -1 && (time - last_send_t[2] >= CAN_MSG_PERIOD_BUTTON)) {
        CanFrame frame = can_encode_msg_button(&dev->button);
        send_can_func(&frame);
        last_send_t[2] = time;
    }
    
}



CanMsgPedals can_decode_msg_pedals(const CanFrame *msg) {
	CanMsgPedals msg_struct = {0};
	msg_struct.acc_pos = can_decode_signal_pedals_acc_pos(msg);
	msg_struct.brake_pos = can_decode_signal_pedals_brake_pos(msg);

	return msg_struct;
}

CanMsgShutdown can_decode_msg_shutdown(const CanFrame *msg) {
	CanMsgShutdown msg_struct = {0};
	msg_struct.error = can_decode_signal_shutdown_error(msg);

	return msg_struct;
}

CanMsgButton can_decode_msg_button(const CanFrame *msg) {
	CanMsgButton msg_struct = {0};
	msg_struct.press = can_decode_signal_button_press(msg);

	return msg_struct;
}

CanFrame can_encode_msg_pedals(const CanMsgPedals *msg) {
	CanFrame message = {.id = 10, .dlc = 2};
	uint64_t word = 0;
	uint64_t *ptr = (uint64_t *) &message.data;

	word |= can_encode_signal_pedals_acc_pos(msg->acc_pos);
	word |= can_encode_signal_pedals_brake_pos(msg->brake_pos);
	
	*ptr = word;
	return message;
}

CanFrame can_encode_msg_shutdown(const CanMsgShutdown *msg) {
	CanFrame message = {.id = 11, .dlc = 1};
	uint64_t word = 0;
	uint64_t *ptr = (uint64_t *) &message.data;

	word |= can_encode_signal_shutdown_error(msg->error);
	
	*ptr = word;
	return message;
}

CanFrame can_encode_msg_button(const CanMsgButton *msg) {
	CanFrame message = {.id = 12, .dlc = 1};
	uint64_t word = 0;
	uint64_t *ptr = (uint64_t *) &message.data;

	word |= can_encode_signal_button_press(msg->press);
	
	*ptr = word;
	return message;
}
