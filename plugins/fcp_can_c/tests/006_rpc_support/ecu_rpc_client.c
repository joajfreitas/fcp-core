#include "ecu_rpc_client.h"

#include "generated_code/ecu_rpc.h"
#include "generated_code/ecu_can.h"

#include <string.h>
#include <stdbool.h>

static CanFrame rpc_response;

static void capture_response(const CanFrame *frame) {
    rpc_response = *frame;
}

bool sensorservice_requeststate(uint8_t *result) {
    CanRpcSensorReq req = {
        .service_id = 0,
        .method_id = 0,
        .request_id = 0x01
    };

    CanFrame request = can_encode_rpc_sensor_req(&req);

    can_service_dispatch_sensor_req(&request, capture_response);

    CanRpcSensorInformation response = can_decode_rpc_sensor_information(&rpc_response);
    *result = response.result;

    return true;
}

void can_service_handle_sensor_req(const CanRpcSensorReq *request, CanRpcSensorInformation *response) {
    te_service_handle(request->method_id, (void *)request, (void *)response);
}

void te_service_handle(uint8_t method_id, void *rpc, void *ans) {
    switch (method_id) {
        case 0: { // RequestState
            CanRpcSensorReq req = *(CanRpcSensorReq *)rpc;
            CanRpcSensorInformation res;

            switch (req.request_id) {
                case 0x01: res.result = 0xA0; break;
                case 0x02: res.result = 0xB0; break;
                case 0x11: res.result = 0xCD; break;
                default:   res.result = 0xFF; break;
            }

            *(CanRpcSensorInformation *)ans = res;
            break;
        }

        case 1: { // GetTemperature
            CanRpcSensorReq req = *(CanRpcSensorReq *)rpc;
            CanRpcTemperatureResponse res;

            switch (req.request_id) {
                case 0x01: res.result = 22; break;
                case 0x02: res.result = 28; break;
                default:   res.result = 0xFF; break;
            }

            *(CanRpcTemperatureResponse *)ans = res;
            break;
        }

        default:

            break;
    }
}