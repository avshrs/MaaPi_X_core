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

class ORM():
    def __init__(self,host,port,id_):
        self.queue              = Queue.Queue()
        self.objectname         = "ORM"
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
        self.selfkill           = False
        self.selfkillTime       = dt.now()
        signal.signal(signal.SIGTERM, self.service_shutdown)
        signal.signal(signal.SIGINT, self.service_shutdown)

    def avalibeInstr(self):
        inst = [ 30:self.maapiDB.insertRaw(),
                 31:self.maapiDB,

        ]

    def service_shutdown(self, signum, frame):
        self.maapilogger.log("STOP",f'Caught signal {signum} | stoping MaaPi {self.objectname}')
        time.sleep(0.5)
        self.maapilogger.log("STOP",f'Self killing - NOW!')
        raise SystemExit()

    def loop(self):
        while True:

            time.sleep(0.01)
            self.checkQueueForReadings()

if __name__ == "__main__":
    ORM_ =  ORM(sys.argv[1],sys.argv[2],sys.argv[3] )
    ORM_.loop()
