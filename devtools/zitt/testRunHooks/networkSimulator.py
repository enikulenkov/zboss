import subprocess
import threading
import logging
import shutil
import os

NS_EXE_RELATIVE_PATH='../../devtools/network_simulator/network_simulator'
def get_ns_exe_path():
    which_res = shutil.which('network_simulator')
    if which_res != None:
        return which_res
    elif os.path.isfile(NS_EXE_RELATIVE_PATH):
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
