MODULE_C_SOURCES := can_signal_parser.c

MODULE_C_SOURCES += $(foreach device, $(CAN_DEVICES), $(device)_can.c)
MODULE_C_SOURCES += $(foreach device, $(CAN_DEVICES), $(device)_can_rpc.c)

CAN2B := $(foreach device, $(CAN_DEVICES), $(PWD)$(device)_can2b.c)
CAN2B_RPC := $(foreach device, $(CAN_DEVICES), $(PWD)$(device)_can2b_rpc.c)

MODULE_C_SOURCES += $(notdir $(wildcard $(CAN2B)))
MODULE_C_SOURCES += $(notdir $(wildcard $(CAN2B_RPC)))

PWD:=lib/can-ids-v2/
C_SOURCES := $(call abs_path,$(MODULE_C_SOURCES),$(PWD))

-include $(PROJECT_ROOT)/build/arch_$(TARGET).mk
