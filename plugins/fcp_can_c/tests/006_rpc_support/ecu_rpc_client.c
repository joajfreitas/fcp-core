#include "ecu_rpc_client.h"

#include "generated_code/ecu_rpc.h"
#include "generated_code/ecu_can.h"

#include <string.h>
#include <stdbool.h>

static CanFrame rpc_response;

static void capture_response(const CanFrame *frame) {
    memcpy(&rpc_response, frame, sizeof(CanFrame));
}

bool sensorservice_requeststate(uint8_t *result) {
    CanRpcSensorReq req = {
        .rpc_id = {.service_id = 0, .method_id = 0},
        .request_id = 0
    };

    CanFrame request = can_encode_rpc_sensor_req(&req);

    can_service_dispatch_sensor_req(&request, capture_response);

    *result = can_decode_rpc_sensor_req(&rpc_response).request_id;
    return true;
}

// RPC handler for SensorService::RequestState
void can_service_handle_sensor_req(const CanRpcSensorReq *request, CanRpcSensorReq *response) {
    response->rpc_id = request->rpc_id;

    switch (request->request_id) {
        case 0x01:
            response->request_id = 0xA0;
            break;
        case 0x02:
            response->request_id = 0xB0;
            break;
        case 0x11:
            response->request_id = 0xCD;
            break;
        default:
            response->request_id = 0xFF;  // erro, desconhecido
            break;
    }
}