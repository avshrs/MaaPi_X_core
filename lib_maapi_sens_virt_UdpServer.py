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

class UdpServer(SensProto):
    def __init__(self,host,port,id_):
        self.id_                = id_
        self.objectname         = "UdpServer"
        self.host               = host
        self.tcpPort            = int(port)
        self.udpPort            = 60000
        self.maapiCommandLine   = []
        self.helpers            = Helpers.Helpers()
        self.timer_1            = dt.now()
        self.timer_2            = dt.now()
        super().__init__()
        self.socketServer.runUdpServer(self.host, self.udpPort)


    def checkQueueForReadings(self):
        try:
            queueTmp  = self.queue.getSocketRadings()
            queue_ = queueTmp[self.objectname][self.host][self.udpPort]

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
                    self.maapilogger.log("INFO",f"Recived id: {nr:<10} |  DevID: {int(queue_[nr][1]):<5} |  Name: {'Recive From UDP':<25} |  Value: {float(float(queue_[nr][2]))} ")

        except EnvironmentError as e :
            self.maapilogger.log("ERROR",f"checkQueueForReadings{e}")


    def loop(self):
        while True:
            time.sleep(0.01)
            self.checkQueueForReadings()


if __name__ == "__main__":
    UdpServer =  UdpServer(sys.argv[1],sys.argv[2],sys.argv[3])
    UdpServer.loop()
