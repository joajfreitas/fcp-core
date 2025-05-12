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

    *result = ((CanRpcSensorReq *)&rpc_response.data)->request_id;
    return true;
}
