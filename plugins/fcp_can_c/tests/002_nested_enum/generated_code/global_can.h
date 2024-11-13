#ifndef GLOBAL_CAN_H
#define GLOBAL_CAN_H

#include <stdint.h>
#include <stdbool.h>

#include "can_frame.h"




typedef enum {
    S0 = 0,
    S1 = 1,
    S2 = 2,
} MyEnum;



/* Check if a CanFrame comes from Global */
bool can_is_global_msg(const CanFrame *frame);



/* Functions to decode CanFrame into CanMsg<name> objects */

/* Functions to encode CanMsg<name> object into CanFrame */

#endif // GLOBAL_CAN_H