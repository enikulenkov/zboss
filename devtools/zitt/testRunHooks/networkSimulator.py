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

import subprocess
import threading
import logging
import shutil
import os

NS_EXE_RELATIVE_PATH='../../devtools/network_simulator/network_simulator'
def get_ns_exe_path():
    # which is not present in Python < 3.3. Temporarily disable it.
    #which_res = shutil.which('network_simulator')
    #if which_res != None:
    #    return which_res
    #elif os.path.isfile(NS_EXE_RELATIVE_PATH):
    if os.path.isfile(NS_EXE_RELATIVE_PATH):
        return NS_EXE_RELATIVE_PATH
    else:
        return None

def _run_ns(device_num, pipe_name):
    dev_null = open('/dev/null')
    ns = subprocess.Popen([get_ns_exe_path(),
                           '--nNode='+str(device_num),
                           '--pipeName='+pipe_name],
                          stdout=dev_null,
                          stderr=subprocess.STDOUT)
    with g_cond:
        g_cond.wait()
    ns.terminate()

def prerun_test(zitt_ctx, test_descr):
    global ns_thread
    global g_cond
    g_cond = threading.Condition()
    device_num = len(test_descr["instances"])
    # TODO: generate pipe_name
    pipe_name = '/tmp/aaa'
    ns_thread = threading.Thread(target=_run_ns, args=(device_num, pipe_name))

    for (i, instance) in zip(range(device_num), test_descr["instances"]):
        if "binary_args" in instance:
            instance["binary_args"].insert(0, pipe_name + str(i) + '.write')
            instance["binary_args"].insert(0, pipe_name + str(i) + '.read')
        else:
            instance["binary_args"] = [pipe_name + str(i) + '.write', pipe_name + str(i) + '.read']
    ns_thread.start()

def postrun_test(zitt_ctx, test_descr):
    with g_cond:
        g_cond.notify()
    ns_thread.join()

def prerun_test_suite(zitt_conf):
    if zitt_conf['device_pool'][0]['type'] != 'linux_ns':
        raise ValueError('Device pool should have type linux_ns')
    if get_ns_exe_path() is None:
        raise EnvironmentError('network_simulator is not found')
    max_instances = zitt_conf['device_pool'][0]['params']['max_instances']
    zitt_conf['device_pool'] = []
    for i in range(max_instances):
        zitt_conf['device_pool'].append({"type" : "linux_process", "params" : {}})

def postrun_test_suite(zitt_conf):
    None
