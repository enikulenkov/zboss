import subprocess
import logging
from .base_device import BaseDevice

class LinuxProcess(BaseDevice):
    def __init__(self, params):
        BaseDevice.init(self, params)
        self.busy = False

    def is_busy(self):
        return self.busy

    def run_instance(self, instance):
        self.instance = instance
        try:
            args = ["stdbuf", "-oL", instance["binary"]]
            if "binary_args" in instance:
                args = args + instance["binary_args"]
                self.child_proc = subprocess.Popen(args, stdout=subprocess.PIPE, bufsize=1)
        except:
            return

        try:
            child_pid = self.child_proc.pid
            logging.info('Instance {} executed'.format(child_pid))

            self.busy = True

            for line in iter(self.child_proc.stdout.readline, b''):
                decoded_line = line.decode('utf-8')
                logging.debug('Proc {} stdout: {}'.format(child_pid, decoded_line))
                if "Device started" in decoded_line:
                    logging.info('Instance {} started successfully'.format(child_pid))
                    self.notify_instance_started()
                elif decoded_line.startswith("Error:"):
                    error_msg = decoded_line.rstrip()[len("Error:"):]
                    logging.info('Error {}'.format(error_msg))
                    self.notify_instance_error(error_msg)
                elif decoded_line.startswith("Warning:"):
                    warn_msg = decoded_line.rstrip()[len("Warning:"):]
                    logging.info('Warning {}'.format(warn_msg))
                    self.notify_instance_warning(warn_msg)

            self.child_proc.wait()
            logging.info('Proc {} ret code {}'.format(child_pid, self.child_proc.returncode))

            self.notify_instance_finished(self.child_proc.returncode)
        except:
            self.stop_instance()

    def stop_instance(self):
        # If child is not terminated yet
        if self.child_proc.poll() == None:
            logging.info("terminating child {}".format(self.child_proc.pid))
            self.child_proc.terminate()
            #TODO: Better error code
            self.notify_instance_finished(1)
