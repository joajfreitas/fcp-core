/** @file can_cfg.c
 *  @brief Configuration Protocol library.
 */

#include <stdlib.h>

#include "can_cfg.h"
#include "can_log.h"
#include "common.h"
#include "can_ids.h"

/** @var uint32_t *cfg_table
 *  @brief Pointer to the array containing the device configuration variables.
 *  Array must be of 32 bit unsigned variables.
 */
uint32_t *cfg_table = 0;

/** @var size_t cfg_size
 *  @brief Size of the configuration table.
 */
size_t cfg_size = 0;

/** @var cfg_configured_lock
 *  @brief Lock configuration handling if module is not configured.
 */
uint8_t cfg_configured_lock = 0;

void cfg_config(uint32_t *table, size_t size) {
	if (table == NULL) {
		return;
	}

	cfg_table = table;
	cfg_size = size;
	cfg_configured_lock = 1;
}

void cfg_dispatch(CANdata msg) {
	if (!cfg_configured_lock) {
		return;
	}

	if (msg.msg_id == MSG_ID_COMMON_REQ_GET) {
		cfg_get_dispatch(msg);
	}

	if (msg.msg_id == MSG_ID_COMMON_REQ_SET) {
		cfg_set_dispatch(msg);
	}
}

void cfg_get_dispatch(CANdata msg) {
	msg_common_req_get_t req_get = decode_common_req_get(msg);

	if (req_get.dst != dev_get_id()) {
		return;
	}

	if (req_get.id >= cfg_size) {
		logE(LOG_WRONG_CFG_ID, 0, 0, 0);
	}
	
	msg_common_ans_get_t ans_get = 
	{
		.dst = req_get.dst,
		.id = req_get.id,
		.data = cfg_table[req_get.id]
	};

	CANdata res = encode_common_ans_get(ans_get, dev_get_id());
	dev_send_msg(res);

	return;	
}

void cfg_set_dispatch(CANdata msg) {
	msg_common_req_set_t req_set = decode_common_req_set(msg);

	if (req_set.dst != dev_get_id()) {
		return;
	}

	if (req_set.id >= cfg_size) {
		logE(LOG_WRONG_CFG_ID, 0, 0, 0);
	}
	
	cfg_table[req_set.id] = req_set.data;

	msg_common_ans_set_t ans_set = 
	{
		.dst = req_set.dst,
		.id = req_set.id,
		.data = cfg_table[req_set.id]
	};

	CANdata res = encode_common_ans_set(ans_set, dev_get_id());
	dev_send_msg(res);

	return;	
}
