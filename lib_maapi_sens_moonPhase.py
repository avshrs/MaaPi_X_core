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

from astral import *

from datetime import datetime as dt
import subprocess

class LinuxCmd():
    def __init__(self,host,port,id_):
        self.queue              = Queue.Queue()
        self.objectname         = "LinuxCmd"
        self.host               = host
        self.port               = int(port)
        self.maapiCommandLine   = []
        self.maapilogger        = MaapiLogger.Logger()
        self.maapilogger.name   = self.objectname
        self.readings           = Readings.Readings(self.objectname,self.host, self.port)
        self.maapiDB            = Db_connection.MaaPiDBConnection()
        self.socketServer       = SocketServer.SocketServer(self.objectname, self.queue,1)
        self.socketServer.runTcpServer(self.host, self.port)

        self.pid                = os.getpid()

        signal.signal(signal.SIGTERM, self.service_shutdown)
        signal.signal(signal.SIGINT, self.service_shutdown)

    def service_shutdown(self, signum, frame):
        self.maapilogger.log("INFO",f'Caught signal {signum} | stoping MaaPi {self.objectname}')
        #self.socketServer.killServers()
        raise SystemExit


    def checkQueueForReadings(self):
        self.readings.checkQueueForReadings(self.readValues, self.queue)


    def readValues(self, que, dev_id, devices_db, devices_db_rel):
        value, error = 0, 0
        try:
            a = Astral()
            location = a['Warsaw'] # finaly data from DB conf table
            timezone = location.timezone
            moon = location.moon_phase(date=dt.now())

            value = round(float(moon) / 14 * 100,0)+(moon/100)+0.001
            if value > 100:
                value = (200 - value)

        except Exception as e:
            return value, 1
            self.maapilogger.log("ERROR", f"Exception read values {self.objectname}: {e}")
        else:
            return value, 0

    def loop(self):
        while True:

            time.sleep(0.01)
            self.checkQueueForReadings()


if __name__ == "__main__":
    LinuxCmd_ =  LinuxCmd(sys.argv[1],sys.argv[2],sys.argv[3] )
    LinuxCmd_.loop()
