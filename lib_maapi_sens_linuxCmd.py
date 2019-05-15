#!/usr/bin/python3.7
# -*- coding: utf-8 -*-import sys
###############################################################
#
#                          MAAPI X
#
##############################################################

from lib_maapi_sens_proto import SensProto
import time, copy, sys, os, signal
from datetime import datetime as dt
import subprocess

class LinuxCmd(SensProto):
    def __init__(self,host,port,id_):
        self.id_                = id_
        self.objectname         = "LinuxCmd"
        self.host               = host
        self.port               = int(port)
        self.maapiCommandLine   = []
        self.timer_1            = dt.now()
        super().__init__()

    def updateCommandLine(self):
        self.maapiCommandLine = self.maapiDB.table("maapi_commandline").columns('cmd_update_rom_id', 'cmd_command').get()
        self.maapilogger.log("DEBUG","Update maapiCommandLine from database")

    def readValues(self, que, dev_id, devices_db, devices_db_rel):
        value, error = 0, 0
        try:
            value = (subprocess.check_output(self.maapiCommandLine[f"{dev_id}"]['cmd_command'],shell=True,)).decode("utf-8")
        except Exception as e:
            self.maapilogger.log("ERROR", f"Exception while read values from  LINUX cmd {self.objectname} - {e} \n {self.maapiCommandLine[dev_id]['cmd_command']}")
            return float(value), 1
        else:
            return float(value), 0

    def service_startup(self):
        self.updateCommandLine()

    def loop(self):
        while self.isRunning:
            if (dt.now() - self.timer_1).seconds >= 10:
                self.timer_1 = dt.now()
                self.updateCommandLine()
            time.sleep(0.01)
            self.responceToWatcher()
            self.checkQueueForReadings()

if __name__ == "__main__":
    LinuxCmd_ =  LinuxCmd(sys.argv[1],sys.argv[2],sys.argv[3] )
    LinuxCmd_.service_startup()
    LinuxCmd_.loop()

