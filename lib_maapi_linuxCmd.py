
#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
##############################################################
#
#                          MAAPI 5.0
#                           Selector
#
##############################################################

import lib_checkDeviceCond                  as CheckDev
import lib_maapi_queue                      as Queue
import lib_maapi_logger                     as MaapiLogger

from datetime import datetime as dt
import sys
import commands


class LinuxCmd(sock):
    def __init__(self):
        self.queue              = Queue.Queue()
        self.checkDev           = CheckDev.CheckDevCond()
        self.maapiCommandLine   = []
        self.timer_1            = dt.now()
        self.timer_2            = dt.now()
        self.maapilogger        = MaapiLogger.Logger()


    def updateCommandLine(self):
        self.maapiCommandLine = maapidb.MaaPiDBConnection().table("maapi_commandline").columns('cmd_update_rom_id', 'cmd_command').get()

    def checkQueueForReadings():


    def readValues(self, data, id):
        try:
            value = commands.getstatusoutput('{0}'.format(self.maapi_commandline[str(arg[0])]['cmd_command']))
            maapidb.MaaPiDBConnection.insert_data(arg[0], float(value[1]), arg[2], True)
        except:
            maapidb.MaaPiDBConnection.insert_data(arg[0], 0, arg[2], False)

    def loop(self):
        while True:
            if (dt.now() - self.timer_1).seconds >=1:
                self.checkQueueForReadings()
                self.timer_1 = dt.now()
            if (dt.now() - self.timer_2).seconds >= 60:
                self.updateCommandLine()
                self.timer_2 = dt.now()
            time.sleep(0.1)
            self.checkDbForOldreadings(self.deviceList)


if __name__ == "__main__":

    LinuxCmd_ =  LinuxCmd()
    LinuxCmd_.runtcpserver()
    LinuxCmd_.updateCommandLine()
    LinuxCmd_.loop()
