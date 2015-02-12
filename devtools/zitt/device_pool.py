from devices import *

class DevicePool:
    def __create_dev(self, device_conf):
        dev_type = device_conf["type"]
        params   = device_conf["params"]

        if (dev_type == 'linux_process'):
            return linux_process.LinuxProcess(params)
        else:
            raise ValueError('Invalid dev type {}'.format(dev_type))

    def __add_device(self, device_conf):
        new_device = self.__create_dev(device_conf)
        self.devices.append(new_device)

    def __init__(self, devices_conf):
        self.devices = []
        for device_conf in devices_conf:
            self.__add_device(device_conf)

    def get_free_device(self):
        ret = None
        for dev in self.devices:
            if not dev.is_busy():
                ret = dev
                break
        return ret
