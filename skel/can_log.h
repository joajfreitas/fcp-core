#ifndef __LOG_CAN_H__
#define __LOG_CAN_H__

#include <stdint.h>
#include "candata.h"

/** @enum log_level_t
 * Logging Levels
 */
typedef enum _log_level_t {
	ERROR,
	WARNING,
	DEBUG,
	INFO
} log_level_t;

/** @fn CANdata log_msg(log_level_t log_level, uint16_t arg1, uint16_t arg2, uint16_t arg3)
 *  @brief Create a CAN packet with a Log Protocol message.
 *  @param log_id Log id
 *  @param arg1 First Log argument
 *  @param arg2 Second Log argument
 *  @param arg3 Third Log argument
 */
CANdata log_msg(log_level_t log_level, uint16_t log_id, uint16_t arg1, uint16_t arg2, uint16_t arg3);

/** @def logE(id, arg1, arg2, arg3) log_msg((ERROR), (id), (arg1), (arg2), (arg3))
 * Create a log with logging level Error
 */
#define logE(id, arg1, arg2, arg3) log_msg((ERROR), (id), (arg1), (arg2), (arg3))

/** @def logW(id, arg1, arg2, arg3) log_msg((WARNING), (id), (arg1), (arg2), (arg3))
 * Create a log with logging level Warning
 */
#define logW(id, arg1, arg2, arg3) log_msg((WARNING), (id), (arg1), (arg2), (arg3))

/** @def logD(id, arg1, arg2, arg3) log_msg((DEBUG), (id), (arg1), (arg2), (arg3))
 * Create a log with logging level Debug
 */
#define logD(id, arg1, arg2, arg3) log_msg((DEBUG), (id), (arg1), (arg2), (arg3))

/** @def logI(id, arg1, arg2, arg3) log_msg((INFO), (id), (arg1), (arg2), (arg3))
 * Create a log with logging level Info
 */
#define logI(id, arg1, arg2, arg3) log_msg((INFO), (id), (arg1), (arg2), (arg3))
#endif
