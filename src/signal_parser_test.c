#include <stdint.h>
#include <stdio.h>

#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

#include <inttypes.h>

#include "minunit.h"
#include "signal_parser.h"

int tests_run = 0;
char message[256] = "";

bool is_equal_double(double value, double check);
bool is_equal_double(double value, double check) {
	return fabs(value - check) < fabs(value)/1000;
}

bool fcp_decode_signal_uint64_t_test_1(void);
bool fcp_decode_signal_uint64_t_test_2(void);
bool fcp_decode_signal_uint64_t_test_3(void);
bool fcp_decode_signal_uint64_t_test_4(void);
bool fcp_decode_signal_uint64_t_test_5(void);
bool fcp_decode_signal_uint64_t_test_6(void);
bool fcp_decode_signal_uint64_t_test_7(void);
bool fcp_decode_signal_uint64_t_test_8(void);
bool fcp_decode_signal_uint64_t_test_9(void);
bool fcp_decode_signal_uint64_t_test_10(void);
bool fcp_decode_signal_uint64_t_big_endian_test_11(void);
bool fcp_decode_signal_uint64_t_big_endian_test_12(void);
bool fcp_decode_signal_uint64_t_big_endian_test_13(void);
bool bitmask_test_14(void);
bool fcp_encode_signal_uint64_t_test_15(void);
bool fcp_encode_signal_uint64_t_test_16(void);
bool fcp_decode_signal_double_test_17(void);
bool fcp_decode_signal_double_big_endian_test_18(void);
#if 0

bool is_equal_double(double value, double check);
bool decode_signal_unsigned_test_1(void);
bool decode_signal_unsigned_test_2(void);
bool decode_signal_unsigned_test_3(void);
bool decode_signal_unsigned_test_4(void);
bool decode_signal_unsigned_test_5(void);
bool decode_signal_unsigned_test_6(void);
bool decode_signal_unsigned_test_7(void);
bool decode_signal_unsigned_test_8(void);
bool decode_signal_unsigned_test_9(void);
bool decode_signal_unsigned_test_10(void);
bool decode_signal_signed_test_11(void);
bool decode_signal_signed_test_12(void);
bool decode_signal_signed_test_13(void);
bool encode_signal_unsigned_test_15(void);
bool encode_signal_unsigned_test_16(void);
bool encode_signal_signed_test_17(void);
bool encode_signal_signed_test_18(void);
bool decode_signal_float_test_19(void);
bool decode_signal_double_test_20(void);
bool encode_signal_float_test_21(void);
bool encode_signal_double_test_22(void);


/* TODO
 *
 */
bool decode_signal_unsigned_test_1(void) {
	uint64_t aux = 0xFFFFFFFFFFFFFFFF;

	CANdata msg;
	uint64_t *ptr = (uint64_t *) msg.data;
	*ptr = aux;
	
	uint64_t *data = (uint64_t *) malloc(sizeof(uint64_t));

	*data = decode_signal_unsigned_as_uint64_t(msg, 0, 64, 1.0, 0);
	mu_assert("test1: unsigned decode 64 bit data", *data == aux);

	return 0;
}


bool decode_signal_unsigned_test_2(void) {
	uint64_t aux = 0xFFFF;

	CANdata msg;
	msg.data[0] = aux;
	
	uint64_t *data = (uint64_t *) malloc(sizeof(uint64_t));

	*data = decode_signal_unsigned_as_uint64_t(msg, 0, 16, 1.0, 0);

	mu_assert("test2: unsigned decode 16 bit data", *(uint16_t *) data == aux);

	return 0;
}

bool decode_signal_unsigned_test_3(void) {
	uint32_t aux = 0xFFFFFFFF;

	CANdata msg;
	uint32_t *ptr = (uint32_t *) (msg.data+1);
	*ptr = aux;
	
	uint64_t *data = (uint64_t *) malloc(sizeof(uint64_t));

	*data = decode_signal_unsigned_as_uint64_t(msg, 16, 48, 1.0, 0);
	mu_assert("test3: unsigned decode 32 bit data shifted", *(uint32_t *) data == aux);

	return 0;
}

bool decode_signal_unsigned_test_4(void) {
	//uint32_t aux = 0x1FFFFFFF;
	uint32_t aux = 1000;

	CANdata msg;
	uint32_t *ptr = (uint32_t *) (msg.data+1);
	*ptr = aux;
	
	uint64_t *data = (uint64_t *) malloc(sizeof(uint64_t));
	*data = decode_signal_unsigned_as_uint64_t(msg, 16, 48, 0.5, 0);
	mu_assert("test4: unsigned decode 32 bit data shifted with scale", is_equal_double(*data, 0.5*(double)aux));

	return 0;
}

bool decode_signal_unsigned_test_5(void) {
	uint32_t aux = 1000;

	CANdata msg;
	uint32_t *ptr = (uint32_t *) (msg.data+1);
	*ptr = aux;
	
	uint64_t *data = (uint64_t *) malloc(sizeof(uint64_t));

	*data = decode_signal_unsigned_as_uint64_t(msg, 16, 48, 2.0, 0);

	mu_assert("test5: unsigned decode 32 bit data shifted with scale", is_equal_double(*data, 2.0*aux));

	return 0;
}

bool decode_signal_unsigned_test_6(void) {
	uint32_t aux = 1000;

	CANdata msg;
	uint32_t *ptr = (uint32_t *) (msg.data+1);
	*ptr = aux;
	
	uint64_t *data = (uint64_t *) malloc(sizeof(uint64_t));

	*data = decode_signal_unsigned_as_uint64_t(msg, 16, 48, 10, 0);

	mu_assert("test6: unsigned decode 32 bit data shifted with scale", is_equal_double(*data, 10.0*aux));

	return 0;
}

bool decode_signal_unsigned_test_7(void) {
	uint32_t aux = 1000;

	CANdata msg;
	uint32_t *ptr = (uint32_t *) (msg.data+1);
	*ptr = aux;
	
	uint64_t *data = (uint64_t *) malloc(sizeof(uint64_t));

	*data = decode_signal_unsigned_as_uint64_t(msg, 16, 48, 0.1, 0);

	mu_assert("test7: unsigned decode 32 bit data shifted with scale", is_equal_double(*(uint32_t *) data, 0.1*aux));

	return 0;
}

bool decode_signal_unsigned_test_8(void) {
	uint32_t aux = 1000;

	CANdata msg;
	uint32_t *ptr = (uint32_t *) (msg.data+1);
	*ptr = aux;
	
	uint64_t *data = (uint64_t *) malloc(sizeof(uint64_t));

	*data = decode_signal_unsigned_as_uint64_t(msg, 16, 48, 100, 0);

	mu_assert("test8: unsigned decode 32 bit data shifted with scale", is_equal_double(*(uint32_t *) data, 100.0*aux));

	return 0;
}

bool decode_signal_unsigned_test_9(void) {
	uint32_t aux = 1000;
	double scale = 0.01;

	CANdata msg;
	uint32_t *ptr = (uint32_t *) (msg.data+1);
	*ptr = aux;
	
	double *data = (double *) malloc(sizeof(double));

	*data = decode_signal_unsigned_as_double(msg, 16, 48, scale, 0);
	mu_assert("test9: unsigned decode 32 bit data shifted with scale", is_equal_double(*data , scale*aux));

	return 0;
}

bool decode_signal_unsigned_test_10(void) {
	CANdata msg;
	uint32_t *ptr = (uint32_t *) (msg.data+1);
	*ptr = 1333;	
	double scale = 1.0;

	for (double i=1e-20; i<=1e20; i*=10) {
		double *data = (double *) malloc(sizeof(double));
		scale = 1.0/(double)i;
		*data = decode_signal_unsigned_as_double(msg, 16, 48, scale, 0);
		mu_assert("test10: unsigned decode 32 bit data shifted with scale",
				is_equal_double(*data, scale*(*ptr)));
	}

	return 0;
}


bool decode_signal_signed_test_11(void) {
	CANdata msg;
	uint32_t *ptr = (uint32_t *) (msg.data+1);
	*ptr = 1333;	
	double scale = 1.0;
	
	for (double i=1e-20; i<=1e20; i*=10) {
		double *data = (double *) malloc(sizeof(double));
		scale = 1.0/(double)i;
		*data = decode_signal_signed_as_double(msg, 16, 48, scale, 0);

		mu_assert("test11: signed decode 32 bit data shifted with scale",
				is_equal_double(*data, scale*(*ptr)));
	}

	return 0;
}


bool decode_signal_signed_test_12(void) {
	CANdata msg;
	int32_t *ptr = (int32_t *) (msg.data+1);
	*ptr = -1333;	
	double scale = 1.0;
	
	double *data = (double *) malloc(sizeof(double));
	for (double i=1e-1; i<=1e20; i*=10) {
		*data = decode_signal_signed_as_double(msg, 16, 48, i, 0);

		mu_assert("test12: signed decode 32 bit data shifted with scale", is_equal_double(*data, i*(*ptr)));
	}

	return 0;
}


bool decode_signal_signed_test_13(void) {
	uint64_t aux = 0xFFFFFFFFFFFFFFFF;

	CANdata msg;
	uint64_t *ptr = (uint64_t *) msg.data;
	*ptr = aux;
	
	int64_t *data = (int64_t *) malloc(sizeof(uint64_t));

	*data = decode_signal_signed_as_int64_t(msg, 0, 64, 1.0, 0);
	mu_assert("test13: signed decode 64 bit data", *data == (int64_t)aux);
	return 0;
}



bool encode_signal_unsigned_test_15(void) {
	uint64_t signal = 10;
	uint64_t *data = (uint64_t *) malloc(sizeof(uint64_t));
	CANdata msg;
	uint64_t *ptr = (uint64_t *) msg.data;

	for (uint64_t i=0; i<12446744073709551615ull; i+=995624215021ull) {
		signal = i;
		*data = encode_signal_unsigned_from_uint64_t(signal, 0, 64, 1.0, 0);
		*ptr = *data;	
		*data = decode_signal_unsigned_as_uint64_t(msg, 0, 64, 1.0, 0);
		mu_assert("test15: unsigned as unsigned encode test", *data == signal);
	}

	return 0;
}

bool encode_signal_unsigned_test_16(void) {
	double signal = 1337.3;
	uint64_t *data1 = (uint64_t *) malloc(sizeof(uint64_t));
	double *data2 = (double *) malloc(sizeof(double));
	CANdata msg;
	uint64_t *ptr = (uint64_t *) msg.data;

	for (double i=1e-8; i<1e-1; i*=10) {
		*data1 = encode_signal_unsigned_from_double(signal, 0, 64, i, 0);
		*ptr = *data1;	
		*data2 = decode_signal_unsigned_as_double(msg, 0, 64, i, 0);
		mu_assert("test16: unsigned as double encode test", *data2 == signal);
	}

	return 0;
}


bool encode_signal_signed_test_17(void) {
	int64_t signal = -10;
	uint64_t *data1 = (uint64_t *) malloc(sizeof(uint64_t));
	int64_t *data2 = (int64_t *) malloc(sizeof(int64_t));
	CANdata msg;
	uint64_t *ptr = (uint64_t *) msg.data;

	for (int64_t i=0; i<2446744073709551615ll; i+=95624215021ll) {
		signal = i;
		*data1 = encode_signal_signed_from_int64_t(signal, 0, 64, 1.0, 0);
		*ptr = *data1;	
		*data2 = decode_signal_signed_as_int64_t(msg, 0, 64, 1.0, 0);
		mu_assert("test17: unsigned as unsigned encode test", *data2 == signal);
	}

	return 0;
}

bool encode_signal_signed_test_18(void) {
	double signal = 1337.3;
	uint64_t *data1 = (uint64_t *) malloc(sizeof(uint64_t));
	double *data2 = (double *) malloc(sizeof(double));
	CANdata msg;
	uint64_t *ptr = (uint64_t *) msg.data;

	for (double i=1e-6; i<1; i*=10) {
		*data1 = encode_signal_signed_from_double(signal, 0, 64, i, 0);
		*ptr = *data1;	
		*data2 = decode_signal_signed_as_double(msg, 0, 64, i, 0);
		mu_assert("test18: unsigned as double encode test", is_equal_double(*data2, signal));
	}

	return 0;
}

bool decode_signal_float_test_19(void) {
	CANdata msg;
	float *ptr = (float *) msg.data;
	ptr[0] = 1337.3;
	float data;
	
	for (double i=1e-20; i < 1e20; i*=10) {
		data = decode_signal_float(msg, 0, 32, i, 0);
		mu_assert("test19: decode float", is_equal_double(i*(*ptr), data));
	}

	return 0;
}

bool decode_signal_double_test_20(void) {
	CANdata msg;
	double *ptr = (double *) msg.data;
	*ptr = 1337.35532413514e23;
	double data;
	
	for (double i=1e-20; i < 1e20; i*=10) {
		data = decode_signal_double(msg, 0, 64, i, 0);
		mu_assert("test20: decode double", is_equal_double(i*(*ptr), data));
	}

	return 0;
}

bool encode_signal_float_test_21(void) {
	CANdata msg;
	uint64_t *ptr = (uint64_t *) &msg.data;
	float value = 1337.3;
	uint64_t data1;
	float data2;
	
	for (double i=1e-20; i < 1e20; i*=10) {
		data1 = encode_signal_float(value, 0, 32, i, 0);
		*ptr = data1;
		data2 = decode_signal_float(msg, 0, 32, i, 0);
		mu_assert("test21: decode float", is_equal_double(value, data2));
	}

	return 0;
}

bool encode_signal_double_test_22(void) {
	CANdata msg;
	uint64_t *ptr = (uint64_t *) &msg.data;
	double value = 1337.3;
	uint64_t data1;
	double data2;
	
	for (double i=1e-20; i < 1e20; i*=10) {
		data1 = encode_signal_double(value, 0, 64, i, 0);
		*ptr = data1;
		data2 = decode_signal_double(msg, 0, 64, i, 0);
		mu_assert("test21: decode float", is_equal_double(value, data2));
	}

	return 0;
}
#endif


bool fcp_decode_signal_uint64_t_test_1(void) {
	uint64_t aux = 0xFFFFFFFFFFFFFFFF;

	CANdata msg;
	uint64_t *ptr = (uint64_t *) msg.data;
	*ptr = aux;
	
	uint64_t data = 0;
	
	fcp_signal_t signal = {
			.start = 0,
			.length = 64,
			.scale = 1.0,
			.offset = 0,
			.type = UNSIGNED,
			.endianess = LITTLE
	};

	data = fcp_decode_signal_uint64_t(msg, signal);
	//printf("%"PRIu64"  %" PRIu64"\n", data, aux);
	mu_assert("test1: unsigned decode 64 bit data", data == aux);

	return 0;
}

bool fcp_decode_signal_uint64_t_test_2(void) {
	uint64_t aux = 0xFFFF;

	CANdata msg;
	msg.data[0] = aux;
	
	fcp_signal_t signal = {
			.start = 0,
			.length = 16,
			.scale = 1.0,
			.offset = 0,
			.type = UNSIGNED,
			.endianess = LITTLE
	};

	uint64_t *data = (uint64_t *) malloc(sizeof(uint64_t));

	*data = fcp_decode_signal_uint64_t(msg, signal);

	mu_assert("test2: unsigned decode 16 bit data", *(uint16_t *) data == aux);

	return 0;
}


bool fcp_decode_signal_uint64_t_test_3(void) {
	uint32_t aux = 0xFFFFFFFF;

	CANdata msg;
	uint32_t *ptr = (uint32_t *) (msg.data+1);
	*ptr = aux;
	
	uint64_t *data = (uint64_t *) malloc(sizeof(uint64_t));

	fcp_signal_t signal = {
			.start = 16,
			.length = 48,
			.scale = 1.0,
			.offset = 0,
			.type = UNSIGNED,
			.endianess = LITTLE
	};

	*data = fcp_decode_signal_uint64_t(msg, signal);
	mu_assert("test3: unsigned decode 32 bit data shifted", *(uint32_t *) data == aux);

	return 0;
}

bool fcp_decode_signal_uint64_t_test_4(void) {
	//uint32_t aux = 0x1FFFFFFF;
	uint32_t aux = 1000;

	CANdata msg;
	uint64_t *ptr = (uint64_t *) msg.data;
	*ptr = aux << 16;
	
	uint64_t *data = (uint64_t *) malloc(sizeof(uint64_t));

	fcp_signal_t signal = {
			.start = 16,
			.length = 48,
			.scale = 0.5,
			.offset = 0,
			.type = UNSIGNED,
			.endianess = LITTLE
	};

	*data = fcp_decode_signal_uint64_t(msg, signal);
	//printf("%"PRIu64 " %lf \n", *data, (0.5*aux));
	mu_assert("test4: unsigned decode 32 bit data shifted with scale", is_equal_double(*data, 0.5*aux));

	return 0;
}

bool fcp_decode_signal_uint64_t_test_5(void) {
	uint32_t aux = 1000;

	CANdata msg;
	uint32_t *ptr = (uint32_t *) (msg.data+1);
	*ptr = aux;
	
	uint64_t *data = (uint64_t *) malloc(sizeof(uint64_t));

	fcp_signal_t signal = {
			.start = 16,
			.length = 48,
			.scale = 2.0,
			.offset = 0,
			.type = UNSIGNED,
			.endianess = LITTLE
	};
	*data = fcp_decode_signal_uint64_t(msg, signal);

	mu_assert("test5: unsigned decode 32 bit data shifted with scale", is_equal_double(*data, 2.0*aux));

	return 0;
}

bool fcp_decode_signal_uint64_t_test_6(void) {
	uint32_t aux = 1000;

	CANdata msg;
	uint32_t *ptr = (uint32_t *) (msg.data+1);
	*ptr = aux;
	
	uint64_t *data = (uint64_t *) malloc(sizeof(uint64_t));

	fcp_signal_t signal = {
			.start = 16,
			.length = 48,
			.scale = 10,
			.offset = 0,
			.type = UNSIGNED,
			.endianess = LITTLE
	};
	*data = fcp_decode_signal_uint64_t(msg, signal);

	mu_assert("test6: unsigned decode 32 bit data shifted with scale", is_equal_double(*data, 10.0*aux));

	return 0;
}

bool fcp_decode_signal_uint64_t_test_7(void) {
	uint32_t aux = 1000;

	CANdata msg;
	uint32_t *ptr = (uint32_t *) (msg.data+1);
	*ptr = aux;
	
	uint64_t *data = (uint64_t *) malloc(sizeof(uint64_t));

	fcp_signal_t signal = {
			.start = 16,
			.length = 48,
			.scale = 0.1,
			.offset = 0,
			.type = UNSIGNED,
			.endianess = LITTLE
	};
	*data = fcp_decode_signal_uint64_t(msg, signal);

	mu_assert("test7: unsigned decode 32 bit data shifted with scale", is_equal_double(*(uint32_t *) data, 0.1*aux));

	return 0;
}

bool fcp_decode_signal_uint64_t_test_8(void) {
	uint32_t aux = 1000;

	CANdata msg;
	uint32_t *ptr = (uint32_t *) (msg.data+1);
	*ptr = aux;
	
	uint64_t *data = (uint64_t *) malloc(sizeof(uint64_t));

	fcp_signal_t signal = {
			.start = 16,
			.length = 48,
			.scale = 100,
			.offset = 0,
			.type = UNSIGNED,
			.endianess = LITTLE
	};
	*data = fcp_decode_signal_uint64_t(msg, signal);

	mu_assert("test8: unsigned decode 32 bit data shifted with scale", is_equal_double(*(uint32_t *) data, 100.0*aux));

	return 0;
}

bool fcp_decode_signal_uint64_t_test_9(void) {
	uint32_t aux = 1000;
	double scale = 0.01;

	CANdata msg;
	uint32_t *ptr = (uint32_t *) (msg.data+1);
	*ptr = aux;
	
	double *data = (double *) malloc(sizeof(double));

	fcp_signal_t signal = {
			.start = 16,
			.length = 48,
			.scale = scale,
			.offset = 0,
			.type = UNSIGNED,
			.endianess = LITTLE
	};
	*data = fcp_decode_signal_uint64_t(msg, signal);
	mu_assert("test9: unsigned decode 32 bit data shifted with scale", is_equal_double(*data , scale*aux));

	return 0;
}

bool fcp_decode_signal_uint64_t_test_10(void) {
	CANdata msg;
	uint32_t *ptr = (uint32_t *) (msg.data+1);
	*ptr = 1333;	

	double scale = 1.0;

	fcp_signal_t signal = {
			.start = 16,
			.length = 48,
			.scale = scale,
			.offset = 0,
			.type = UNSIGNED,
			.endianess = LITTLE
	};

	int j=0;
	for (double i=1e-15; i<=1; i*=10) {
		double *data = (double *) malloc(sizeof(double));
		scale = 1.0/(double)i;
		signal.scale = scale;
		*data = fcp_decode_signal_uint64_t(msg, signal);

		mu_assert("test10: unsigned decode 32 bit data shifted with scale",
				is_equal_double(*data, scale*(*ptr)));
		j++;
	}

	return 0;
}

bool fcp_decode_signal_uint64_t_big_endian_test_11(void) {
	CANdata msg;
	uint64_t *ptr = (uint64_t *) (msg.data);

	*ptr = 0x0011223344556677;

	fcp_signal_t signal = {
			.start = 0,
			.length = 64,
			.scale = 1.0,
			.offset = 0,
			.type = UNSIGNED,
			.endianess = BIG
	};

	uint64_t data = fcp_decode_signal_uint64_t(msg, signal);
	mu_assert("test11: unsigned decode 64 bit data big endian",
			data == 0x7766554433221100);

	return 0;
}

bool fcp_decode_signal_uint64_t_big_endian_test_12(void) {
	CANdata msg;
	uint64_t *ptr = (uint64_t *) (msg.data);

	*ptr = 0x0000445566770000;

	fcp_signal_t signal = {
			.start = 16,
			.length = 32,
			.scale = 1.0,
			.offset = 0,
			.type = UNSIGNED,
			.endianess = BIG
	};

	uint64_t data = fcp_decode_signal_uint64_t(msg, signal);
	mu_assert("test11: unsigned decode 64 bit data big endian",
			data == 0x77665544);

	return 0;
}

bool fcp_decode_signal_uint64_t_big_endian_test_13(void) {
	CANdata msg;
	uint64_t *ptr = (uint64_t *) (msg.data);

	*ptr = 0x0000000066770000;

	fcp_signal_t signal = {
			.start = 16,
			.length = 16,
			.scale = 1.0,
			.offset = 0,
			.type = UNSIGNED,
			.endianess = BIG
	};

	uint64_t data = fcp_decode_signal_uint64_t(msg, signal);
	mu_assert("test11: unsigned decode 64 bit data big endian",
			data == 0x7766);

	return 0;
}

bool bitmask_test_14(void) {
	uint64_t mask = 0;
	for (unsigned int i=0; i<=64; i++) {
		mask = 0;
		for (unsigned int j=0; j<i; j++) {
			mask |= 1ULL << j;
		}

		mu_assert("test14: bitmask check", mask == bitmask(i));
	}

	return 0;
}


bool fcp_encode_signal_uint64_t_test_15(void) {
	uint64_t value = 10;
	uint64_t *data = (uint64_t *) malloc(sizeof(uint64_t));
	CANdata msg;
	uint64_t *ptr = (uint64_t *) msg.data;

	fcp_signal_t signal = {
			.start = 0,
			.length = 64,
			.scale = 1.0,
			.offset = 0,
			.type = UNSIGNED,
			.endianess = LITTLE
	};

	for (uint64_t i=0; i<12446744073709551615ull; i+=995624215021ull) {
		value = i;
		*data = fcp_encode_signal_uint64_t(value, signal);
		*ptr = *data;	
		*data = fcp_decode_signal_uint64_t(msg, signal);
		mu_assert("test15: unsigned as unsigned encode test", *data == value);
	}

	return 0;
}


bool fcp_encode_signal_uint64_t_test_16(void) {
	uint64_t value = 10;
	uint64_t *data = (uint64_t *) malloc(sizeof(uint64_t));
	CANdata msg;
	uint64_t *ptr = (uint64_t *) msg.data;

	fcp_signal_t signal = {
			.start = 0,
			.length = 64,
			.scale = 1.0,
			.offset = 0,
			.type = UNSIGNED,
			.endianess = BIG,
	};

	for (uint64_t i=0; i<12446744073709551615ull; i+=995624215021ull) {
		value = i;
		*data = fcp_encode_signal_uint64_t(value, signal);
		*ptr = *data;	
		*data = fcp_decode_signal_uint64_t(msg, signal);
		mu_assert("test15: unsigned as unsigned encode test", *data == value);
	}

	return 0;
}

bool fcp_decode_signal_double_test_17(void) {
	uint16_t aux = 10001;
	
	fcp_signal_t signal = {
		.start = 0,
		.length = 16,
		.scale = 0.01,
		.offset = 0,
		.type = UNSIGNED,
		.endianess = LITTLE
	};

	
	CANdata msg;
	uint64_t *ptr = (uint64_t *) msg.data;
	*ptr = aux;
	
	double data = fcp_decode_signal_double(msg, signal);
	printf("%lf %lf\n", data, 0.01*aux);
	mu_assert("test1: decode double with scaling", data == 0.01*aux);

	return 0;
}

bool fcp_decode_signal_double_big_endian_test_18(void) {
	uint16_t aux = 0x1127;
	
	fcp_signal_t signal = {
		.start = 0,
		.length = 16,
		.scale = 0.01,
		.offset = 0,
		.type = UNSIGNED,
		.endianess = BIG
	};

	
	CANdata msg;
	uint64_t *ptr = (uint64_t *) msg.data;
	*ptr = aux;
	
	double data = fcp_decode_signal_double(msg, signal);

	mu_assert("test1: decode double with scaling", data == 100.01);

	return 0;
}

static char *all_tests() {
	mu_run_test(fcp_decode_signal_uint64_t_test_1);
	mu_run_test(fcp_decode_signal_uint64_t_test_2);
	mu_run_test(fcp_decode_signal_uint64_t_test_3);
	mu_run_test(fcp_decode_signal_uint64_t_test_4);
	mu_run_test(fcp_decode_signal_uint64_t_test_5);
	mu_run_test(fcp_decode_signal_uint64_t_test_6);
	mu_run_test(fcp_decode_signal_uint64_t_test_7);
	mu_run_test(fcp_decode_signal_uint64_t_test_8);
	mu_run_test(fcp_decode_signal_uint64_t_test_9);
	mu_run_test(fcp_decode_signal_uint64_t_test_10);
	mu_run_test(fcp_decode_signal_uint64_t_big_endian_test_11);
	mu_run_test(fcp_decode_signal_uint64_t_big_endian_test_12);
	mu_run_test(fcp_decode_signal_uint64_t_big_endian_test_13);
	mu_run_test(bitmask_test_14);
	mu_run_test(fcp_encode_signal_uint64_t_test_15);
	mu_run_test(fcp_encode_signal_uint64_t_test_16);
	mu_run_test(fcp_decode_signal_double_test_17);
	mu_run_test(fcp_decode_signal_double_big_endian_test_18);
    return 0;
}

int main() {
	char *result = all_tests();
	if (result != 0) {
		printf("===============================================================\nFAILED: %s\n===============================================================\n", result);
	}
    else {
		printf("===============================================================\nALL TESTS PASSED \n===============================================================\n");
	}
    printf("Tests run: %d\n", tests_run);

	return result != 0;
}
