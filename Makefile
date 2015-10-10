#/***************************************************************************
#*                      ZBOSS ZigBee Pro 2007 stack                         *
#*                                                                          *
#*          Copyright (c) 2012 DSR Corporation Denver CO, USA.              *
#*                       http://www.dsr-wireless.com                        *
#*                                                                          *
#*                            All rights reserved.                          *
#*          Copyright (c) 2011 ClarIDy Solutions, Inc., Taipei, Taiwan.     *
#*                       http://www.claridy.com/                            *
#*                                                                          *
#*          Copyright (c) 2011 Uniband Electronic Corporation (UBEC),       *
#*                             Hsinchu, Taiwan.                             *
#*                       http://www.ubec.com.tw/                            *
#*                                                                          *
#*          Copyright (c) 2011 DSR Corporation Denver CO, USA.              *
#*                       http://www.dsr-wireless.com                        *
#*                                                                          *
#*                            All rights reserved.                          *
#*                                                                          *
#*                                                                          *
#* ZigBee Pro 2007 stack, also known as ZBOSS (R) ZB stack is available     *
#* under either the terms of the Commercial License or the GNU General      *
#* Public License version 2.0.  As a recipient of ZigBee Pro 2007 stack, you*
#* may choose which license to receive this code under (except as noted in  *
#* per-module LICENSE files).                                               *
#*                                                                          *
#* ZBOSS is a registered trademark of DSR Corporation AKA Data Storage      *
#* Research LLC.                                                            *
#*                                                                          *
#* GNU General Public License Usage                                         *
#* This file may be used under the terms of the GNU General Public License  *
#* version 2.0 as published by the Free Software Foundation and appearing   *
#* in the file LICENSE.GPL included in the packaging of this file.  Please  *
#* review the following information to ensure the GNU General Public        *
#* License version 2.0 requirements will be met:                            *
#* http://www.gnu.org/licenses/old-licenses/gpl-2.0.html.                   *
#*                                                                          *
#* Commercial Usage                                                         *
#* Licensees holding valid ClarIDy/UBEC/DSR Commercial licenses may use     *
#* this file in accordance with the ClarIDy/UBEC/DSR Commercial License     *
#* Agreement provided with the Software or, alternatively, in accordance    *
#* with the terms contained in a written agreement between you and          *
#* ClarIDy/UBEC/DSR.                                                        *
#*                                                                          *
#****************************************************************************
#PURPOSE:
#*/

include Options
include Platform
include Makefile.helpers

.PHONY: tests mk_obj_dir.% devtools

all: libs tests

MODULES := common mac nwk osif/$(PLATFORM) secur aps zdo
TESTS   := tests/aib_nib_pib_test \
	         tests/aps_dup_reject \
	         tests/aps_group \
					 tests/certification/TP_APS_BV-09 \
					 tests/certification/TP_APS_BV-12-I \
					 tests/certification/TP_APS_BV-27-I \
					 tests/certification/TP_APS_BV-29-I \
					 tests/certification/TP_APS_BV-35-I \
					 tests/certification/TP_NWK_BV-12 \
					 tests/certification/TP_PRO_BV-26 \
					 tests/certification/TP_PRO_BV-35 \
					 tests/certification/TP_PRO_BV-36 \
					 tests/nwk_best_route \
					 tests/nwk_leave \
					 tests/nwk_passive_ack \
					 tests/nwk_status \
					 tests/orphan_scan \
					 tests/remove_device \
					 tests/zdo_active_ep \
					 tests/zdo_addr \
					 tests/zdo_intra_pan_portability \
					 tests/zdo_join_duration \
					 tests/zdo_lqi \
					 tests/zdo_mgmt_join_time \
					 tests/zdo_mgmt_nwk \
					 tests/zdo_start_secur \
					 tests/zdo_startup

zboss_CONFS   :=
zboss_SRCS    :=
zboss_TESTS   :=

OBJ_DIR := .objs

# Two default configurations added automatically:
# coordinator and end device.
$(eval $(call add_config,include/zb_config.zc.h,zc))
$(eval $(call add_config,include/zb_config.ze.h,ze))

# include Makefile for each module
include $(patsubst %, %/Makefile.sub, $(MODULES))
include $(patsubst %, %/Makefile.sub, $(TESTS))

# Libs to build. One for each configuration. 
zboss_LIBS := $(foreach conf, $(zboss_CONFS), $(call libzboss_name,$(conf)))

# Set variables containing object files and deps files per configuration
$(foreach conf, $(zboss_CONFS), $(eval $(call config_vars,$(conf))))
# Generate rules for building every object file
$(foreach conf, $(zboss_CONFS), $(call gen_obj_rules,$(conf)))
# Include deps files
-include $(foreach conf, $(zboss_CONFS), $(zboss_$(conf)_DEPS))

# Generate rules for building every test object file
$(foreach conf, $(zboss_CONFS), $(call gen_test_obj_rules,$(conf)))
# Include deps for tests
test_DEPS := $(foreach conf, $(zboss_CONFS), $(call gen_test_deps,$(conf)))
-include $(test_DEPS)

tests: $(zboss_TESTS)

libs: $(zboss_LIBS)

# Create directory for object files
mk_obj_dir.%:
	$(Q)mkdir -p `echo $* | tr ',' '/'`

.SECONDEXPANSION:
libzboss.%.a: $$(zboss_$$*_OBJS)
	@echo AR $@
	$(Q)$(AR) r $@ $^

clean:
	@echo "Cleaning up..."
	$(Q)for i in $(MODULES); \
		do rm -f $$i/$(OBJ_DIR)/*.o $$i/$(OBJ_DIR)/*.d $$i/*.a;\
	done
	$(Q)rm -f $(foreach conf, $(zboss_CONFS), $(test_$(conf)_OBJS))
	$(Q)rm -f $(foreach conf, $(zboss_CONFS), $(test_$(conf)_OBJS:.o=.d))
	$(Q)rm -f $(zboss_TESTS)
	$(Q)rm -f libzboss.*.a
	@echo "Finished"

clobber: clean
	rm -f TAGS tags BROWSE

etags:
	($(FIND) . -name \*.[ch] -print) | grep -v ".*~" | etags -

ctags:
	($(FIND) . -name \*.[ch] -print) | grep -v ".*~" | ctags -I ZB_CALLBACK,ZB_SDCC_REENTRANT,ZB_SDCC_BANKED -L -

rebuild: clean all

docs: doc_api doc_int

doc_int:
	rm -rf doxydoc_int
	doxygen Doxyfile.INT

doc_api:
	rm -rf doxydoc_api
	doxygen Doxyfile.API

devtools:
	( cd devtools/dump_converter && make )
	( cd devtools/network_simulator && make )

run-st: libs tests
	( cd devtools/zitt && zitt -c defaults/default_conf.json -l defaults/all_tests.list )
