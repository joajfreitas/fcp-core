#include "ecu_can.h"
#include "can_signal_parser.h"

/*-------------------- Decode Signals ---------------------*/
// Foo
#define can_decode_signal_foo_s1(msg) \
    can_decode_signal_as_uint8_t((msg), 0, 8, 1.0, 0.0)
#define can_decode_signal_foo_s2(msg) \
    can_decode_signal_as_uint16_t((msg), 8, 16, 1.0, 0.0)
#define can_decode_signal_foo_s3(msg) \
    can_decode_signal_as_uint8_t((msg), 24, 2, 1.0, 0.0)
/*---------------------------------------------------------*/

/*-------------------- Encode Signals ---------------------*/
// Foo
#define can_encode_signal_foo_s1(signal) \
    can_encode_signal_from_uint8_t((signal), 0, 8, 1.0, 0.0);
#define can_encode_signal_foo_s2(signal) \
    can_encode_signal_from_uint16_t((signal), 8, 16, 1.0, 0.0);
#define can_encode_signal_foo_s3(signal) \
    can_encode_signal_from_uint8_t((signal), 24, 2, 1.0, 0.0);
/*---------------------------------------------------------*/

bool can_is_ecu_msg(const CanFrame *frame) {
    return
        frame->id == CAN_MSG_ID_FOO;
}


void can_send_ecu_msgs_scheduled(const CanDeviceEcu *dev, uint32_t time, void (*send_can_func)(const CanFrame *)) {
    static uint32_t last_call_t = 0;
    static uint32_t last_send_t[1] = {0};

    if (last_call_t == time) return;
    last_call_t = time;

    // Check if enough time has passed for Foo
    if (CAN_MSG_PERIOD_FOO != -1 && (time - last_send_t[0] >= CAN_MSG_PERIOD_FOO)) {
        CanFrame frame = can_encode_msg_foo(&dev->foo);
        send_can_func(&frame);
        last_send_t[0] = time;
    }
    
}



CanMsgFoo can_decode_msg_foo(const CanFrame *msg) {
	CanMsgFoo msg_struct = {0};
	msg_struct.s1 = can_decode_signal_foo_s1(msg);
	msg_struct.s2 = can_decode_signal_foo_s2(msg);
	msg_struct.s3 = can_decode_signal_foo_s3(msg);

	return msg_struct;
}

CanFrame can_encode_msg_foo(const CanMsgFoo *msg) {
	CanFrame message = {.id = 10, .dlc = 4};
	uint64_t word = 0;
	uint64_t *ptr = (uint64_t *) &message.data;

	word |= can_encode_signal_foo_s1(msg->s1);
	word |= can_encode_signal_foo_s2(msg->s2);
	word |= can_encode_signal_foo_s3(msg->s3);
	
	*ptr = word;
	return message;
}
