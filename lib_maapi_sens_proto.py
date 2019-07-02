 #!/usr/bin/python3.7
# -*- coding: utf-8 -*-import sys
###############################################################
#
#                          MAAPI X
#
##############################################################
import time
import copy
import sys
import os
import signal
import lib_maapi_main_checkDevCond as CheckDev
import lib_maapi_main_queue as Queue
import lib_maapi_main_logger as MaapiLogger
import lib_maapi_main_socketClient as SocketClient
import lib_maapi_main_socketServer as SocketServer
import lib_maapi_main_helpers as Helpers
import lib_maapi_main_dbconn as Db_connection
import lib_maapi_main_readings as Readings

from datetime import datetime as dt


class SensProto():
    def __init__(self):
        self.objectname = "none"
        self.host = ""
        self.port = 0
        self.id_ = ""
        self.readings = object
        self.socketServer = object
        self.isRunning = True
        self.queue = Queue.Queue()
        self.helpers = Helpers.Helpers()
        self.socketClient = SocketClient.socketClient()
        self.maapilogger = MaapiLogger.Logger()
        self.maapiDB = Db_connection.MaaPiDBConnection()

        signal.signal(signal.SIGTERM, self.service_shutdown)
        signal.signal(signal.SIGINT, self.service_shutdown)

    def readValues(self):
        pass

    def libInit(self):
        self.readings = Readings.Readings(self.objectname, self.host, self.port)
        self.maapilogger.name = self.objectname
        self.payload_Status_responce = self.helpers.pyloadToPicke(
            0xff, " ", " ", " ", self.host, self.port)
        self.socketServer = SocketServer.SocketServer(
            self.objectname,
            self.queue,
            self.id_
            )
        self.socketServer.runTcpServer(self.host, self.port)

    def service_shutdown(self, signum, frame):
        self.isRunning = False
        self.maapilogger.log(
            "STOP",
            f'Caught signal {signum} | stoping MaaPi'
            f' {self.objectname}'
            )
        raise SystemExit

    def responceToWatcher(self):
        if self.queue.getSocketStatusLen() > 0:
            queue_ = (self.queue.getSocketStatus())[self.objectname][self.host][self.port]
            for nr in queue_:
                if queue_[nr][0] == 0:
                    try:
                        self.maapilogger.log(
                            "DEBUG",
                            f"Sending responce to Wacher"
                            f" {queue_[nr][4]} {queue_[nr][5]}"
                            )
                        self.socketClient.sendStr(
                            queue_[nr][4],
                            queue_[nr][5],
                            self.payload_Status_responce
                            )
                    except:
                         self.maapilogger.log(
                             "ERROR",
                             f"Watcher Socket Server Not exist"
                             )
                # elif queue_[nr][0] == 777:
                    # self.maapilogger.log("ERROR", f"Get self kill instruction via queue")
                    # self.service_shutdown()

    def checkQueueForReadings(self):
        self.readings.checkQueueForReadings(self.readValues, self.queue)
