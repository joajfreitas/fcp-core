#include "stdio.h"
#include "stdint.h"
#include "stdbool.h"
#include "stdlib.h"
#include <string.h>
#include <unistd.h>

#include <net/if.h>
#include <sys/ioctl.h>
#include <sys/socket.h>

#include <linux/can.h>
#include <linux/can/raw.h>

int send_frame(int socket, struct can_frame* frame) {
    if (write(socket, frame, sizeof(struct can_frame)) != sizeof(struct can_frame)) {
		perror("Write");
		return 1;
	}

    return 0;
}

int send_first_frame(int socket, uint8_t* data, uint16_t len, uint16_t* index) {
	struct can_frame frame;

    frame.can_id = 0x1;
	frame.can_dlc = 8;

    frame.data[0] = (1 << 4) | (len >> 8);
    frame.data[1] = len & 0xff;
    frame.data[2] = data[0];
    frame.data[3] = data[1];
    frame.data[4] = data[2];
    frame.data[5] = data[3];
    frame.data[6] = data[4];
    frame.data[7] = data[5];

    *index += 6;
    return send_frame(socket, &frame);

}

int send_consequent_frame(int socket, uint8_t* data, uint16_t len, uint16_t* index, uint8_t* seq) {
	struct can_frame frame;

    frame.can_id = 0x1;

    frame.data[0] = (2 << 4) | *seq;

    printf("index: %d\n", *index);
    int i=0;
    for (; i<7 && *index + i < len; i++) {
        frame.data[i+1] = data[*index+i];

    }

	frame.can_dlc = i+1;

    *seq = (*seq + 1) & 0xF;
    *index += i;

    return send_frame(socket, &frame);
}

int send_flow_control_frame(int socket) {
	struct can_frame frame;
    frame.can_id = 0x2;
    frame.can_dlc = 3;
    frame.data[0] = (3 << 4);
    frame.data[1] = 0;
    frame.data[2] = 0;
    return send_frame(socket, &frame);
}

int main() {
	int s;
    struct sockaddr_can addr;
	struct ifreq ifr;
	struct can_frame frame;

	if ((s = socket(PF_CAN, SOCK_RAW, CAN_RAW)) < 0) {
		perror("Socket");
		return 1;
	}

    strcpy(ifr.ifr_name, "vcan0" );
	ioctl(s, SIOCGIFINDEX, &ifr);

    memset(&addr, 0, sizeof(addr));
	addr.can_family = AF_CAN;
	addr.can_ifindex = ifr.ifr_ifindex;

    if (bind(s, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
		perror("Bind");
		return 1;
	}

    uint16_t len = 0;
    uint16_t expected_len = 0xFF;
    uint8_t data[4096] = {0};

    while (true) {
	    int nbytes = read(s, &frame, sizeof(struct can_frame));
        uint8_t flow_control_code = frame.data[0] >> 4;
        if (flow_control_code == 0x1) {
            for (int i=0; i<6; i++) {
                data[len++] = frame.data[i+2];
            }

            expected_len = (((uint16_t) frame.data[0] & 0xF << 8)  + (uint16_t) frame.data[1]);
            send_flow_control_frame(s);
        }
        if (flow_control_code == 0x2) {
            for (int i=0; i<frame.can_dlc -  1; i++) {
                data[len++] = frame.data[i+2];
            }
        }

        printf("progress: %d %d\n", len, expected_len);
        if (expected_len == len) {
            break;
        }
    }

    for (int i=0; i<len-1; i++) {
        printf("%x ", data[i]);
    }

    printf("\n");

    //send_first_frame(s, data, len, &index);

    //seq += 1;

	//int nbytes = read(s, &frame, sizeof(struct can_frame));

    //if (frame.can_id != 2) {
    //    printf("Expected id 2");
    //    return 1;
    //}
    //else if (frame.data[0] != 3 << 4){
    //    printf("Expected control byte to be 3");
    //    return 1;
    //}


    //while (index < len) {
    //    send_consequent_frame(s, data, len, &index, &seq);
    //}

    //printf("index: %d", index);
    //if (close(s) < 0) {
	//	perror("Close");
	//	return 1;
	//}

    return 0;
}
