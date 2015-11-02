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
