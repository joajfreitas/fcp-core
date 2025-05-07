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
    CanFrame request = {
        .id = ECU_RPC_GET_ID,
        .dlc = 3
    };

    RpcMethod *method = (RpcMethod *) &request.data[0];
    method->service = SENSOR_SERVICE_ID;
    method->method = 1;

    can_service_dispatch(&request, capture_response);

    *result = rpc_response.data[2];
    return true;
}
