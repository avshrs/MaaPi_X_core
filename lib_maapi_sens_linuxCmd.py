#!/usr/bin/python3.7
# -*- coding: utf-8 -*-import sys
###############################################################
#
#                          MAAPI X
#
##############################################################

import lib_maapi_main_checkDevCond               as CheckDev
import lib_maapi_main_queue                      as Queue
import lib_maapi_main_logger                     as MaapiLogger
import lib_maapi_main_socketClient               as SocketClient
import lib_maapi_main_socketServer               as SocketServer
import lib_maapi_main_helpers                    as Helpers
import lib_maapi_main_dbORM                      as Db_connection
import lib_maapi_main_readings                   as Readings
import time, copy, sys, os, signal

from datetime import datetime as dt
import subprocess

class LinuxCmd():
    def __init__(self,host,port,id_):
        self.queue              = Queue.Queue()
        self.objectname         = "LinuxCmd"
        self.host               = host
        self.port               = int(port)
        self.maapiCommandLine   = []
        self.timer_1            = dt.now()
        self.timer_2            = dt.now()
        self.maapilogger        = MaapiLogger.Logger()
        self.maapilogger.name   = self.objectname
        self.readings           = Readings.Readings(self.objectname,self.host, self.port)
        self.maapiDB            = Db_connection.MaaPiDBConnection()
        self.socketServer       = SocketServer.SocketServer(self.objectname, self.queue,1)
        self.socketServer.runTcpServer(self.host, self.port)

        self.selfkill           = False
        self.selfkillTime       = dt.now()
        signal.signal(signal.SIGTERM, self.service_shutdown)
        signal.signal(signal.SIGINT, self.service_shutdown)



    def service_shutdown(self, signum, frame):
        if not self.selfkill:
            self.maapilogger.log("STOP",f'Caught signal {signum} | stoping MaaPi {self.objectname}')
            self.selfkill = True
            self.selfkillTime = dt.now()

    def selfkilling(self):
        if self.selfkill and (dt.now() - self.selfkillTime).seconds >2:
            self.maapilogger.log("STOP",f'Reading modules Not Raise self term. - SocketServer not running self killing')
            raise SystemExit



    def updateCommandLine(self):
        self.maapiCommandLine = self.maapiDB.table("maapi_commandline").columns('cmd_update_rom_id', 'cmd_command').get()
        self.maapilogger.log("DEBUG","Update maapiCommandLine from database")


    def checkQueueForReadings(self):
        self.readings.checkQueueForReadings(self.readValues, self.queue)


    def readValues(self, que, dev_id, devices_db, devices_db_rel):
        value, error = 0, 0
        try:
            value = (subprocess.check_output(self.maapiCommandLine[f"{dev_id}"]['cmd_command'],shell=True,)).decode("utf-8")
        except Exception as e:
            return float(value), 1
            self.maapilogger.log("ERROR", f"Exception while read values from  LINUX cmd {self.objectname} - {e} \n {self.maapiCommandLine[dev_id]['cmd_command']}")
        else:
            return float(value), 0

    def loop(self):
        while True:
            if (dt.now() - self.timer_2).seconds >= 10:
                self.timer_2 = dt.now()
                self.updateCommandLine()
            time.sleep(0.01)
            self.checkQueueForReadings()
            self.selfkilling()

if __name__ == "__main__":
    LinuxCmd_ =  LinuxCmd(sys.argv[1],sys.argv[2],sys.argv[3] )
    LinuxCmd_.updateCommandLine()
    LinuxCmd_.loop()
