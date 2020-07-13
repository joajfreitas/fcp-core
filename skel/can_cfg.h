/** @file can_cfg.h
 *  @brief Configuration Protocol library.
 */

#ifndef __CAN_CFG_H__
#define __CAN_CFG_H__

#include <stdint.h>
#include <stdlib.h>

#include "candata.h"


/** @fn void cfg_config(uint32_t *table, size_t size)
 *  @brief Configure the Configuration Protocol library.
 *  @param table Configs table.
 *  @param size Size of configs table.
 */
void cfg_config(uint32_t *table, size_t size);

/** @fn void cfg_dispatch(CANdata msg)
 *  @brief Handle configuration requests.
 *  @param msg Received CAN frame.
 */
void cfg_dispatch(CANdata msg);

/** @fn void cfg_get_dispatch(CANdata msg)
 *  @brief Handle GET configuration requests.
 *	@param msg Received CAN frame.
 */
void cfg_get_dispatch(CANdata msg);

/** @fn void cfg_set_dispatch(CANdata msg)
 *  @brief Handle SET configuration requests.
 *  @param msg Received CAN frame.
 */
void cfg_set_dispatch(CANdata msg);

#endif /* ifndef __CAN_CFG_H__ */
