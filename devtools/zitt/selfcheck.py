#!/usr/bin/env python3
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

import unittest
import imp
from device_pool import DevicePool
import zitt_common

zitt = imp.load_source('zitt', './zitt')

class TestZittStatistics(unittest.TestCase):

    def setUp(self):
        zitt.init_zitt_ctx(zitt.zitt, {})

    def create_fake_device_pool(self, device_num):
        device_pool = []
        for i in range(device_num):
            device_pool.append({"type" : "fake", "params" : {}})
        zitt.zitt['device_pool'] = DevicePool(device_pool)

    def test_simple(self):
        self.create_fake_device_pool(1)
        zitt.run_test_by_descr({ "name" : "simple",
            "instances" : [{ "binary" : "none", "test_role" : "dut", "init_level" : 0,
                             "modifiers": [] }],
            "timeout" : 1})
        self.assertDictEqual({"tests_executed" : 1, "tests_failed" : 0, "errors_count" : 0,
            "warnings_count" : 0}, zitt.zitt['stats'])

    def test_timeout(self):
        self.create_fake_device_pool(1)
        zitt.run_test_by_descr({ "name" : "timeout",
                "instances" : [{ "binary" : "none", "test_role" : "dut", "init_level" : 0,
                                 "modifiers" : ["NeverFinish"]}],
                "timeout" : 0.1})
        self.assertDictEqual({"tests_executed" : 1, "tests_failed" : 1, "errors_count" : 0,
            "warnings_count" : 0}, zitt.zitt['stats'])

    def test_instance_non_zero_return_code(self):
        self.create_fake_device_pool(1)
        zitt.run_test_by_descr({ "name" : "non_zero_code",
                "instances" : [{ "binary" : "none", "test_role" : "dut", "init_level" : 0,
                                 "modifiers" : ["ReturnError"] }],
                "timeout" : 1})
        self.assertDictEqual({"tests_executed" : 1, "tests_failed" : 1, "errors_count" : 0,
            "warnings_count" : 0}, zitt.zitt['stats'])

    def test_instance_reports_error(self):
        self.create_fake_device_pool(1)
        zitt.run_test_by_descr({ "name" : "instance_reports_error",
                "instances" : [{ "binary" : "none", "test_role" : "dut", "init_level" : 0,
                                 "modifiers" : ["ReportError"] }],
                "timeout" : 1})
        self.assertDictEqual({"tests_executed" : 1, "tests_failed" : 1, "errors_count" : 1,
            "warnings_count" : 0}, zitt.zitt['stats'])

    def test_instance_reports_warning(self):
        self.create_fake_device_pool(1)
        zitt.run_test_by_descr({ "name" : "instance_reports_warning",
                "instances" : [{ "binary" : "none", "test_role" : "dut", "init_level" : 0,
                                 "modifiers" : ["ReportWarning"] }],
                "timeout" : 1})
        self.assertDictEqual({"tests_executed" : 1, "tests_failed" : 0, "errors_count" : 0,
            "warnings_count" : 1}, zitt.zitt['stats'])

    def test_instance_never_starts(self):
        self.create_fake_device_pool(1)
        zitt.run_test_by_descr({ "name" : "instance_never_starts",
                "instances" : [{ "binary" : "none", "test_role" : "dut", "init_level" : 0,
                                 "modifiers" : ["NoStartNotification", "NeverFinish"] }],
                "timeout" : 0.1})
        self.assertDictEqual({"tests_executed" : 1, "tests_failed" : 1, "errors_count" : 0,
            "warnings_count" : 0}, zitt.zitt['stats'])

    def test_finish_without_start_notification(self):
        self.create_fake_device_pool(1)
        zitt.run_test_by_descr({ "name" : "finish_without_start_notification",
                "instances" : [{ "binary" : "none", "test_role" : "dut", "init_level" : 0,
                                 "modifiers" : ["NoStartNotification"] }],
                "timeout" : 1})
        self.assertDictEqual({"tests_executed" : 1, "tests_failed" : 1, "errors_count" : 0,
            "warnings_count" : 0}, zitt.zitt['stats'])

    def test_instance_reports_error_and_warning(self):
        self.create_fake_device_pool(1)
        zitt.run_test_by_descr({ "name" : "finish_without_start_notification",
                "instances" : [{ "binary" : "none", "test_role" : "dut", "init_level" : 0,
                                 "modifiers" : ["ReportError", "ReportWarning"] }],
                "timeout" : 1})
        self.assertDictEqual({"tests_executed" : 1, "tests_failed" : 1, "errors_count" : 1,
            "warnings_count" : 1}, zitt.zitt['stats'])


if __name__ == '__main__':
    #zitt.enable_logging(True, True)
    unittest.main()
