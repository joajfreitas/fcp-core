/** @file can_cmd.c
 *  @brief Command Protocol library.
 */

#include "can_cmd.h"
#include "can_ids.h"
#include "common.h"

CANdata cmd_send(
		uint64_t cmd, 
		uint64_t dst, 
		uint64_t arg1, 
		uint64_t arg2,
		uint64_t arg3)
{
	msg_common_send_cmd_t send_common_aux = 
	{
			.id = cmd,
			.dst = dst,
			.arg1 = arg1,
			.arg2 = arg2,
			.arg3 = arg3
		};

	return encode_common_send_cmd(send_common_aux, dev_get_id());
}

CANdata cmd_return(multiple_return_t mt) {
	msg_common_return_cmd_t return_cmd = 
	{
		.ret1 = mt.arg1,
		.ret2 = mt.arg2,
		.ret3 = mt.arg3
	};

	return encode_common_return_cmd(return_cmd, dev_get_id());
}

void cmd_dispatch(CANdata msg) {
	if (msg.msg_id != MSG_ID_COMMON_SEND_CMD) {
		return;
	}
	msg_common_send_cmd_t cmd = decode_common_send_cmd(msg);

	if (cmd.dst != dev_get_id()) {
		return;
	}

	multiple_return_t mt;
	mt = cmd_handle(cmd.id, cmd.arg1, cmd.arg2, cmd.arg3);
	
	CANdata return_msg = cmd_return(mt);
	dev_send_msg(return_msg);
}
