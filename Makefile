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

.PHONY: tests setconf.%

all: libs tests

MODULES := common mac nwk osif/$(PLATFORM) secur aps zdo
#TESTS   := tests/aib_nib_pib_test

zboss_SRCS    :=
zboss_TESTS   :=
zboss_CONFS   :=

OBJ_DIR := .objs

# Two default configurations added automatically:
# coordinator and end device.
$(eval $(call add_config,include/zb_config.zc.h,zc))
$(eval $(call add_config,include/zb_config.ze.h,ze))

# include Makefile for each module
include $(patsubst %, %/Makefile.sub, $(MODULES))
#include $(patsubst %, %/Makefile.sub, $(TESTS))

# Libs to build. One for each configuration. 
zboss_LIBS := $(foreach conf, $(zboss_CONFS), $(call libzboss_name,$(conf)))

# Set variables containing object files and deps files per configuration
$(foreach conf, $(zboss_CONFS), $(eval $(call config_vars,$(call get,conf_h2n,$(conf)))))
# Generate rules for building every object file
$(foreach conf, $(zboss_CONFS), $(call gen_obj_rules,$(call get,conf_h2n,$(conf))))
# Include deps files
-include $(foreach conf, $(zboss_CONFS), $(zboss_$(call get,conf_h2n,$(conf))_DEPS))

#tests: $(zboss_TESTS)

libs: $(zboss_LIBS)

# Given name of configuration copy its config header file as include/zb_config.h
setconf.%:
	$(Q)CONF_PATH=$(call get,conf_n2h,$*) ; \
	if [ \( ! -L include/zb_config.h -o \
	        x`readlink include/zb_config.h` != x$$CONF_PATH \) -a \
 	      -f $$CONF_PATH ] ; then \
		ln -sf ../$$CONF_PATH include/zb_config.h ; \
	fi;

# Create directory for object files
mk_obj_dir.%:
	$(Q)mkdir -p $*

.SECONDEXPANSION:
libzboss.%.a: $$(zboss_$$*_OBJS) | setconf.$$*
	@echo AR $@
	$(Q)$(AR) r $@ $^

clean:
	for i in $(MODULES); \
		do rm -f $$i/$(OBJ_DIR)/*.o $$i/$(OBJ_DIR)/*.d $$i/*.a;\
	done
	rm -f libzboss.*.a

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
