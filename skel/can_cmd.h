/** @file can_cmd.h
 *  @brief Command Protocol library.
 */

#ifndef __CAN_CMD_H__
#define __CAN_CMD_H__

#include "candata.h"
#include "common.h"

typedef struct _multiple_return_t {
	uint16_t arg1;
	uint16_t arg2;
	uint16_t arg3;
} multiple_return_t;

/** @fn CANdata cmd_send(uint64_t cmd, uint64_t dst, uint64_t arg1, uint64_t arg2, uint64_t arg3)
 *	@brief Create a CAN packet with a Command message.
 *	@param cmd Command id.
 *	@param dst Destination device id.
 *	@param arg1 first command argument
 *	@param arg2 second command argument
 *	@param arg3 third command argument
 */
CANdata cmd_send(
		uint64_t cmd, 
		uint64_t dst, 
		uint64_t arg1, 
		uint64_t arg2,
		uint64_t arg3);

/** @fn void cmd_dispatch(CANdata msg)
 *  @brief Handle a command request.
 *  @param msg CAN message packet.
 */
void cmd_dispatch(CANdata msg);

/** @fn multiple_return_t cmd_handle(uint16_t id, uint16_t arg1, uint16_t arg2, uint16_t arg3)
 *  @brief User side handling of the command request.
 *  @param id Command id.
 *  @param arg1 First command argument
 *  @param arg2 Second command argument
 *  @param arg2 Third command argument
 */
multiple_return_t cmd_handle(uint16_t id, uint16_t arg1, uint16_t arg2, uint16_t arg3);

#endif /* ifndef __CAN_CMD_H__ */
