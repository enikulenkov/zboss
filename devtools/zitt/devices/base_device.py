import threading
import logging

class BaseDevice:
    def __init__(self, params):
        self.listeners = []
        self.lock      = threading.Lock()

    def add_listener(self, listener):
        logging.debug("add listener {}".format(listener))
        with self.lock:
            self.listeners.append(listener)

    def remove_listener(self, listener):
        logging.debug("remove listener {}".format(listener))
        with self.lock:
            self.listeners.remove(listener)

    def notify_instance_started(self):
        for listener in self.listeners:
            listener.instance_started_event(self.instance)

    def notify_instance_error(self, msg):
        for listener in self.listeners:
            listener.instance_error_event(self.instance, msg)

    def notify_instance_warning(self, msg):
        for listener in self.listeners:
            listener.instance_warning_event(self.instance, msg)

    def notify_instance_finished(self, return_code):
        for listener in self.listeners:
            listener.instance_finished_event(self.instance, return_code)
