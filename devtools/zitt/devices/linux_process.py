import threading
import subprocess
import shlex
import logging

class LinuxProcess:
    def __init__(self, params):
        self.listeners = []
        self.busy      = False
        self.lock      = threading.Lock()

    def is_busy(self):
        return self.busy

    def run_instance(self, instance):
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

    def add_listener(self, listener):
        with self.lock:
            self.listeners.append(listener)

    def remove_listener(self, listener):
        with self.lock:
            self.listeners.remove(listener)

    def notify_instance_started(self):
        for listener in self.listeners:
            listener.instance_started_event()

    def notify_instance_error(self, msg):
        for listener in self.listeners:
            listener.instance_error_event(msg)

    def notify_instance_warning(self, msg):
        for listener in self.listeners:
            listener.instance_warning_event(msg)

    def notify_instance_finished(self, return_code):
        for listener in self.listeners:
            listener.instance_finished_event(return_code)
