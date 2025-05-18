#ifndef ECU_RPC_CLIENT_H
#define ECU_RPC_CLIENT_H

#include <stdint.h>
#include <stdbool.h>

#include "generated_code/ecu_rpc.h"
#include "generated_code/can_frame.h"

/* Chamada de alto nível (cliente) */
bool sensorservice_requeststate(uint8_t *result);

/* Handler chamado pelo dispatcher gerado */
void can_service_handle_sensor_req(const CanRpcSensorReq *request, CanRpcSensorInformation *response);

/* Handler definido pelo utilizador para todos os métodos do SensorService */
void te_service_handle(uint8_t method_id, void *rpc, void *ans);

#endif // ECU_RPC_CLIENT_H
