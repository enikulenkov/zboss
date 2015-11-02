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

import threading
import logging

import zitt_common

class TestRunner:
    class InstanceExecutor:
        def __init__(self, device, instance):
            self.device   = device
            self.instance = instance
            self.sem      = threading.Semaphore(0)
            self.mutex    = threading.Lock()
            self.finished = False
            self.result   = {'name'            : instance['binary'],
                             'errors'          : [],
                             'warnings'        : [],
                             'dev_return_code' : 'undefined'}

        def _clear(self):
            self.finished = True
            self.sem.release()
            self.device.remove_listener(self)
            logging.debug('instance {} finished'.format(self.tid))

        def instance_started_event(self):
            logging.debug('instance started event {}'.format(self.tid))
            with self.mutex:
                self.sem.release()

        def instance_error_event(self, msg):
            with self.mutex:
                self.result['errors'].append(msg)

        def instance_warning_event(self, msg):
            with self.mutex:
                self.result['warnings'].append(msg)

        def instance_finished_event(self, return_code):
            logging.debug('instance finished event {}'.format(self.tid))
            with self.mutex:
                if self.result['dev_return_code'] == 'undefined':
                    self.result['dev_return_code'] = str(return_code)
                    self._clear()

        def __start_instance(self):
            self.device.run_instance(self.instance)

        def start_instance(self):
            self.device.add_listener(self)
            self.tid = threading.Thread(target=self.__start_instance)
            self.tid.start()
            self.sem.acquire()
            logging.debug('instance {} started'.format(self.tid))
            return self.result['dev_return_code'] in ('undefined', '0')

        def stop_instance(self):
            with self.mutex:
                logging.info("stop_instance...")
                self.device.stop_instance()
                self._clear()

        def wait_instance_finish(self):
            if not self.finished:
                self.sem.acquire()
            return self.result

    def __init__(self, descr):
        self.test_timeout = descr['timeout']
        self.test_descr   = descr
        self.dev_threads  = []
        self.mutex        = threading.Lock()
        self.result       = {'result' : zitt_common.RET_SUCCESS, 'instances' : []}

    def run_devices(self, device_pool):
        try:
            descr = self.test_descr
            print("running test {}".format(descr["name"]))

            for instance in sorted(descr["instances"], key = lambda x: x["start_idx"]):
                device = device_pool.get_free_device()
                executor = self.InstanceExecutor(device, instance)
                self.dev_threads.append(executor)
                ret = executor.start_instance()

                with self.mutex:
                    if self.result['result'] == zitt_common.RET_SUCCESS:
                        if ret != True:
                            logging.debug('Startup error')
                            self.result['result'] = zitt_common.RET_STARTUP_ERROR
                            self.stop_devices()
                            break
                    else:
                        # Timeout has happened, break the loop
                        break
        except KeyboardInterrupt:
            self.result['result'] = zitt_common.RET_STOPPED_BY_USER
        except:
            self.result['result'] = zitt_common.RET_INTERNAL_ERROR

        finally:
            for executor in self.dev_threads:
                instance_res = executor.wait_instance_finish()
                self.result['instances'].append(instance_res)

        return self.result

    def stop_devices(self):
        logging.info("Stop devices")
        for executor in self.dev_threads:
            if not executor.finished:
                executor.stop_instance()
        logging.debug("Devices stopped")

    def test_timeout_timer(self):
        logging.info("Timeout")
        with self.mutex:
            self.result['result'] = zitt_common.RET_TIMEOUT
            self.stop_devices()

    def run(self, device_pool):
        t = threading.Timer(self.test_timeout, self.test_timeout_timer, )
        t.start()
        ret = self.run_devices(device_pool)
        t.cancel()
        return ret
