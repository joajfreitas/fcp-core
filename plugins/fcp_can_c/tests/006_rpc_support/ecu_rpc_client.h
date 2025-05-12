#ifndef ECU_RPC_CLIENT_H
#define ECU_RPC_CLIENT_H

#include <stdbool.h>
#include <stdint.h>

#include "generated_code/ecu_rpc.h"
#include "generated_code/can_frame.h"

#define SENSOR_SERVICE_ID 1

/* SensorService RPC Methods */
bool sensorservice_requeststate(uint8_t *result);

/* For test compatibility */
#define CALL_MY_RPC sensorservice_requeststate

#endif // ECU_RPC_CLIENT_H
