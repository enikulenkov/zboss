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
import logging
import signal
import os
from .base_device import BaseDevice

class LinuxProcess(BaseDevice):
    def __init__(self, params):
        BaseDevice.__init__(self, params)
        self.busy = False

    def is_busy(self):
        return self.busy

    def gdb_command_file_create(self, instance_pid):
        self_dir = os.path.dirname(os.path.realpath(__file__))
        out_file_path = os.path.realpath(self_dir + "/../etc/gdbinit-current")
        template_path = os.path.realpath(self_dir + "/../etc/gdbinit-template")
        with open(out_file_path, "wt") as out_file:
            with open(template_path, "rt") as template:
                for line in template:
                    out_file.write(line.replace('$(pid)', str(instance_pid)))
        return out_file_path

    def debug_preexec(self):
        pid = os.getpid()
        gdb_cmdfile_path = self.gdb_command_file_create(pid)
        logging.error('Instance {} with PID {} is running under debug.\n'
                      'You can attach to it using the following command:\n'
                      'gdb -x {}'.format(self.instance["binary"], pid, gdb_cmdfile_path))
        os.kill(pid, signal.SIGSTOP)

    def run_instance(self, instance):
        self.instance = instance
        self.busy = True
        try:
            args = [instance["binary"]]
            if "binary_args" in instance:
                args = args + instance["binary_args"]
            preexec_fn = self.debug_preexec if "debug" in instance else None
            self.child_proc = subprocess.Popen(args, stdout=subprocess.PIPE,
                    bufsize=1, preexec_fn = preexec_fn)
        except:
            logging.exception("can't run device {}".format(instance["binary"]))
            return

        try:
            child_pid = self.child_proc.pid
            logging.info('Instance {} executed'.format(child_pid))

            self.busy = True

            for line in iter(self.child_proc.stdout.readline, b''):
                decoded_line = line.decode('utf-8')
                logging.debug('Proc {} stdout: {}'.format(child_pid, decoded_line))
                if "Device started OK" in decoded_line:
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
        finally:
            self.stop_instance()

    def stop_instance(self):
        # If child is not terminated yet
        if self.child_proc.poll() == None:
            logging.info("terminating child {}".format(self.child_proc.pid))
            self.child_proc.terminate()
            #TODO: Better error code
            self.notify_instance_finished(1)
        self.busy = False
