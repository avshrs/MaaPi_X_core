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
import time, copy, sys

from datetime import datetime as dt
import sys
import subprocess

class UdpServer():
    def __init__(self,host,port,id_):
        self.queue              = Queue.Queue()
        self.objectname         = "UdpServer"
        self.host               = host
        self.port               = port
        self.maapiCommandLine   = []
        self.helpers            = Helpers.Helpers()
        self.timer_1            = dt.now()
        self.timer_2            = dt.now()
        self.maapilogger        = MaapiLogger.Logger()
        self.maapilogger.name   = self.objectname
        self.readings           = Readings.Readings(self.objectname,self.host, self.port)
        self.maapiDB            = Db_connection.MaaPiDBConnection()
        self.socketServer       = SocketServer.SocketServer(self.objectname, self.queue, id_)
        self.socketServer.runTcpServer(self.host, self.port+1)
        self.socketServer.runUdpServer(self.host, self.port)


    def checkQueueForReadings(self):
        try:
            queueTmp  = self.queue.getSocketRadings()
            queue_ = queueTmp[self.objectname][self.host][self.port]

            for nr in queue_:
                payload_id          = queue_[nr][0]
                dev_id              = queue_[nr][1]
                devices_db          = queue_[nr][2]
                devices_db_rel      = queue_[nr][3]

                self.maapilogger.log("DEBUG",f"payload_id: {payload_id}")
                self.maapilogger.log("DEBUG",f"dev_id: {dev_id}")
                self.maapilogger.log("DEBUG",f"devices_db: {devices_db}")
                self.maapilogger.log("DEBUG",f"devices_db_rel: {devices_db_rel}")

                if int(queue_[nr][0]) == self.helpers.instructions["recive_from_UDP"]:
                    self.maapiDB.insert_readings(int(queue_[nr][1]),float(queue_[nr][2])," ",True)
                    self.maapilogger.log("INFO",f"Recived id: {nr:<10} DevID: {int(queue_[nr][1]):<8} Name: {'Recive From UDP':<20} \tValue: {float(float(queue_[nr][2]))} ")

        except EnvironmentError as e :
            self.maapilogger.log("ERROR",f"checkQueueForReadings{e}")


    def loop(self):
        while True:
            time.sleep(0.01)
            self.checkQueueForReadings()


if __name__ == "__main__":
    UdpServer =  UdpServer(sys.argv[1],sys.argv[2],sys.argv[3])
    UdpServer.loop()
