#ifndef _CANDATA
#define _CANDATA
typedef struct {
	union {
        struct {
			uint16_t dev_id:5; // Least significant
			// First bit of msg_id determines if msg is reserved or not.
			// 0 == reserved (higher priority) (0-31 decimal)
			uint16_t msg_id:6; // Most significant
		};
		uint16_t sid;
	};
	uint16_t dlc:4;
	uint16_t data[4];
} CANdata;
#endif
