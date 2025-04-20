#include "ecu_rpc_client.h"

#include "generated_code/ecu_rpc.h"
#include "generated_code/ecu_can.h"

#include <string.h>
#include <stdbool.h>

static CanFrame rpc_response;

static void capture_response(const CanFrame *frame) {
    memcpy(&rpc_response, frame, sizeof(CanFrame));
}

bool request_sensor_state(uint8_t *result) {
    CanFrame request;
    request.id = ECU_RPC_GET_ID;
    request.dlc = 8;

    RpcMessage *msg = (RpcMessage *) request.data;
    msg->id.rpc_id = 0;
    memset(msg->args, 0, sizeof(msg->args));

    /* Add the can_service_dispatch function declaration from can_service.h */
    bool handled = can_service_dispatch(&request, capture_response);
    if (!handled) return false;

    RpcMessage *res = (RpcMessage *) rpc_response.data;
    *result = res->args[0];
    return true;
}
