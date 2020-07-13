#include <stdint.h>
#include <stdio.h>

#include "munit.h"
#include "candata.h"
#include "can_ids.h"
#include "can_cmd.h"
#include "can_cfg.h"

uint16_t cmd_return_var;

uint16_t dev_get_id() {
	return 10;
}

void dev_send_msg(CANdata msg) {
	printf("CANdata (%d, %d, %d,", msg.dev_id, msg.msg_id, msg.dlc);
	for (int i=0; i<msg.dlc/2; i++) {
		printf("%d, ", msg.data[i]);
	}
	printf(")\n");
	cmd_return_var = msg.data[1];
}

multiple_return_t cmd_handle(
		uint16_t id,
		uint16_t arg1,
		uint16_t arg2,
		uint16_t arg3)
{

	multiple_return_t mt;
	mt.arg1 = 1;
	mt.arg2 = 2;
	mt.arg3 = 3;

	//if (id == CMD_CCU_FAN) {
	//	mt.arg1 = 10;
	//}


	return mt;
}

static MunitResult test_encode_decode(const MunitParameter params[], void* data) {
	dev_te_t te;

	msg_te_te_main_t te_main = {0};
	te_main.apps = 100.0;
	te_main.bps_pressure = 80.0;
	te_main.bps_electric = 90.0;
	
	CANdata message = encode_329(te_main);

	munit_assert_uint(message.dev_id, ==,  9);
	munit_assert_uint(message.msg_id, ==, 10);
	uint64_t word = *((uint64_t *) &message.data);
	munit_assert_uint((word >> 16) & 0xFFFF, ==, 10000);

	decode_te(message, &te);
	
	munit_assert_double_equal(te.te_main.apps, 100.0, 10);
	munit_assert_double_equal(te.te_main.bps_pressure, 80.0, 10);
	munit_assert_double_equal(te.te_main.bps_electric, 90.0, 10);
	
	for (int i=0; i<100; i++) {
		te_send_msgs(te, i);
	}

	return MUNIT_OK;
}

static MunitResult test_encode_decode_mux(const MunitParameter params[], void* data) {
	dev_bms_verbose_t verbose;

	msg_bms_verbose_bms_cell_inf_t cell_inf = {0};
	cell_inf.id = 10;
	cell_inf.soc[10] = 100.0;
	cell_inf.t[10] = 100,0;
	cell_inf.t_state[10] = 1;
	cell_inf.v[10] = 3.7;
	cell_inf.v_state[10] = 1;
	
	CANdata message = encode_2031(cell_inf);

	munit_assert_uint(message.dev_id, ==,  15);
	munit_assert_uint(message.msg_id, ==, 63);

	decode_bms_verbose(message, &verbose);
	
	munit_assert_uint(verbose.bms_cell_inf.id, =, 10);
	munit_assert_double_equal(verbose.bms_cell_inf.soc[10], 100.0, 10);
	munit_assert_double_equal(verbose.bms_cell_inf.t[10], 100.0, 10);
	munit_assert_uint(verbose.bms_cell_inf.t_state[10], =, 1);
	munit_assert_double_equal(verbose.bms_cell_inf.v[10], 3, 10);
	munit_assert_uint(verbose.bms_cell_inf.v_state[10], =, 1);

	return MUNIT_OK;
}


static MunitResult test_encode_decode_common(const MunitParameter params[], void* data) {

	msg_common_log_t log = {0};
	log.level = 2;
		
	CANdata message = encode_common_log(log, 13);

	munit_assert_uint(message.dev_id, ==,  13);
	munit_assert_uint(message.msg_id, ==, MSG_ID_COMMON_LOG);
	
	dev_common_t dev_common;
	decode_common(message, &dev_common);
	
	munit_assert_uint(dev_common.log.level, =, 2);

	return MUNIT_OK;
}

static MunitResult test_cmd_dispatch(const MunitParameter params[], void* data) {
	//msg_common_send_cmd_t send_cmd = {
	//	.dst = dev_get_id(),
	//	.id = CMD_CCU_FAN,
	//	.arg1 = 1,
	//	.arg2 = 2,
	//	.arg3 = 3
	//};

	//CANdata msg = encode_common_send_cmd(send_cmd, 0);

	//cmd_dispatch(msg);
	//munit_assert_int16(cmd_return_var, ==, 10);

	return MUNIT_OK;
}

static MunitResult test_cfg_dispatch(const MunitParameter params[], void* data) {

	uint32_t configs[3] = {0};
	cfg_config(configs, 3);

	msg_common_req_set_t req_set = {
		.dst = dev_get_id(),
		.id = 0,
		.data = 10,
	};

	CANdata msg = encode_common_req_set(req_set, 0);

	cfg_dispatch(msg);
	munit_assert_int16(configs[0], ==, 10);
	
	return MUNIT_OK;
}

static MunitTest test_suite_tests[] = {
  {
	  (char*) "decode_encode1",
	  test_encode_decode,
	  NULL,
	  NULL,
	  MUNIT_TEST_OPTION_NONE,
	  NULL
  },
  {
	  (char*) "encode_decode_mux",
	  test_encode_decode_mux,
	  NULL,
	  NULL,
	  MUNIT_TEST_OPTION_NONE,
	  NULL
  },
  {
	  (char*) "encode_decode_common",
	  test_encode_decode_common,
	  NULL,
	  NULL,
	  MUNIT_TEST_OPTION_NONE,
	  NULL
  },
  {
	  (char*) "cmd_dispatch",
	  test_cmd_dispatch,
	  NULL,
	  NULL,
	  MUNIT_TEST_OPTION_NONE,
	  NULL
  },
  {
	  (char*) "cfg_dispatch",
	  test_cfg_dispatch,
	  NULL,
	  NULL,
	  MUNIT_TEST_OPTION_NONE,
	  NULL
  },
  { 
	  NULL, 
	  NULL, 
	  NULL, 
	  NULL, 
	  MUNIT_TEST_OPTION_NONE, 
	  NULL 
  }
};

static const MunitSuite test_suite = {
  (char*) "",
  test_suite_tests,
  NULL,
  1,
  MUNIT_SUITE_OPTION_NONE
};

int main(int argc, char *argv[])
{
	return munit_suite_main(&test_suite, (void*) "µnit", argc, argv);
}
