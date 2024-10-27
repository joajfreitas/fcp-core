#include "stdio.h"
#include "stdint.h"
#include "stdbool.h"
#include "stdlib.h"
#include <string.h>
#include <unistd.h>
#include <fcntl.h>

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

typedef enum {
    Started,
    InProgress,
    Waiting,
    Finished,
} Status;

typedef struct {
    uint8_t* buffer;
    uint16_t len;
    uint8_t seq;
    uint16_t index;
    Status status;
} IsoTpSender;

IsoTpSender init_sender_buffer(uint8_t* data, uint16_t len) {
    return (IsoTpSender) { 
        .buffer = data,
        .len = len,
        .seq = 0,
        .index = 0,
        .status = Started,
    };
}

uint8_t next_byte(IsoTpSender* buffer) {
    return buffer->buffer[buffer->index++];
}

Status send_data(IsoTpSender* buffer, int socket) {
	struct can_frame frame;

    frame.can_id = 0x1;
    if (buffer->status == Waiting) {
        return buffer->status;
    }
    else if (buffer->status == Started) {
        if (buffer->len <= 6) {
            frame.can_dlc = buffer->len + 2;
            buffer->status = Finished;
        }
        else {
            frame.can_dlc = 8;
            buffer->status = InProgress;
        }

        for (int i = 0; i<6 && i < buffer->len; i++) {
            frame.data[i+2] = next_byte(buffer);
        }

        frame.data[0] = (1 << 4) | (buffer->len >> 8);
        frame.data[1] = buffer->len & 0xff;
    }
    else if (buffer->status == InProgress) {
        int i=0;
        for (; i<7 && buffer->index<buffer->len; i++) {
            frame.data[i+1] = next_byte(buffer);
        }

        if (buffer->len == buffer->index) {
            buffer->status = Finished;
        }

        buffer->seq = (buffer->seq + 1) & 0xf;
        frame.data[0] = 2<<4 | buffer->seq;
        frame.can_dlc = i+1;
    }

    send_frame(socket, &frame);

    return buffer->status;
}


//int send_first_frame(int socket, uint8_t* data, uint16_t len, uint16_t* index) {
//	struct can_frame frame;
//
//    frame.can_id = 0x1;
//	frame.can_dlc = 8;
//
//    frame.data[0] = (1 << 4) | (len >> 8);
//    frame.data[1] = len & 0xff;
//    frame.data[2] = data[0];
//    frame.data[3] = data[1];
//    frame.data[4] = data[2];
//    frame.data[5] = data[3];
//    frame.data[6] = data[4];
//    frame.data[7] = data[5];
//
//    send_frame(socket, &frame);
//
//    *index += 6;
//}
//
//int send_consequent_frame(int socket, uint8_t* data, uint16_t len, uint16_t* index, uint8_t* seq) {
//	struct can_frame frame;
//
//    frame.can_id = 0x1;
//
//    frame.data[0] = (2 << 4) | *seq;
//
//    printf("index: %d\n", *index);
//    int i=0;
//    for (; i<7 && *index + i < len; i++) {
//        frame.data[i+1] = data[*index+i];
//
//    }
//
//	frame.can_dlc = i+1;
//
//    *seq = (*seq + 1) & 0xF;
//    *index += i;
//
//    send_frame(socket, &frame);
//}

int main(int argc, char* argv[]) {
	int s;
    struct sockaddr_can addr;
	struct ifreq ifr;
	struct can_frame frame;

	if ((s = socket(PF_CAN, SOCK_RAW, CAN_RAW)) < 0) {
		perror("Socket");
		return 1;
	}

    fcntl(s, F_SETFL, O_NONBLOCK);

    strcpy(ifr.ifr_name, argv[1]);
	ioctl(s, SIOCGIFINDEX, &ifr);

    memset(&addr, 0, sizeof(addr));
	addr.can_family = AF_CAN;
	addr.can_ifindex = ifr.ifr_ifindex;

    if (bind(s, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
		perror("Bind");
		return 1;
	}

    uint16_t len = 149;
    uint8_t data[149] = {
        0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x10, 0x11, 0x12,
        0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x20, 0x21, 0x22, 0x23, 0x24,
        0x25, 0x26, 0x27, 0x28, 0x29, 0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36,
        0x37, 0x38, 0x39, 0x40, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48,
        0x49, 0x50, 0x51, 0x52, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58, 0x59, 0x60,
        0x61, 0x62, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68, 0x69, 0x70, 0x71, 0x72,
        0x73, 0x74, 0x75, 0x76, 0x77, 0x78, 0x79, 0x80, 0x81, 0x82, 0x83, 0x84,
        0x85, 0x86, 0x87, 0x88, 0x89, 0x90, 0x91, 0x92, 0x93, 0x94, 0x95, 0x96,
        0x97, 0x98, 0x99, 0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5, 0xA6, 0xA7, 0xA8,
        0xA9, 0xB0, 0xB1, 0xB2, 0xB3, 0xB4, 0xB5, 0xB6, 0xB7, 0xB8, 0xB9, 0xC0,
        0xC1, 0xC2, 0xC3, 0xC4, 0xC5, 0xC6, 0xC7, 0xC8, 0xC9, 0xD0, 0xD1, 0xD2,
        0xD3, 0xD4, 0xD5, 0xD6, 0xD7, 0xD8, 0xD9, 0xE0, 0xE1, 0xE2, 0xE3, 0xE4,
        0xE5, 0xE6, 0xE7, 0xE8, 0xE9};


    IsoTpSender sender_buffer = init_sender_buffer(data, len);
    
    while(true) {
	    int nbytes = read(s, &frame, sizeof(struct can_frame));

        if (nbytes != 0) {
            receive_msg(&sender_buffer, frame);
        }
        Status status = send_data(&sender_buffer, s);
        if (status == Finished) {
            break;
        }
    }


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
