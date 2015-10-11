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
            self.sem.release()
            self.finished = True
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
            return self.result['dev_return_code'] == 'undefined'

        def stop_instance(self):
            with self.mutex:
                logging.info("stop_instance..")
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
