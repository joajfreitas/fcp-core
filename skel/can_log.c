/** @file can_log.c
 *  @brief Log Protocol library.
 */

#include "can_log.h"
#include "can_ids.h"

/** @fn CANdata log_msg(log_level_t log_level, uint16_t arg1, uint16_t arg2, uint16_t arg3)
 *  @brief Create a CAN packet with a Log Protocol message.
 *  @param log_id Log id
 *  @param arg1 First Log argument
 *  @param arg2 Second Log argument
 *  @param arg3 Third Log argument
 */
CANdata log_msg(
		log_level_t log_level, 
		uint16_t log_id, 
		uint16_t arg1, 
		uint16_t arg2, 
		uint16_t arg3
) {
	msg_common_log_t log_config;
	log_config.level = log_level;
	log_config.n_args = 3;
	log_config.err_code = log_id;
	log_config.arg1 = arg1;
	log_config.arg2 = arg2;
	log_config.arg3 = arg3;

	CANdata msg = encode_common_log(log_config, dev_get_id());
	return msg;	
}
