#!/usr/bin/python3.7
# -*- coding: utf-8 -*-import sys
###############################################################
#
#                          MAAPI X
#
##############################################################
from Adafruit_BME280 import *

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

class BME280I2C():
    def __init__(self,host,port,id_):
        self.queue              = Queue.Queue()
        self.objectname         = "BME_280"
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
        value = 0
        error = 0
        # 1 - temp
        # 2 - hum
        # 4 - press
        unit_id = devices_db[dev_id]['dev_unit_id']

        if unit_id == 1:
            sensor = BME280(p_mode=BME280_OSAMPLE_8)
            value = float(sensor.read_temperature())

        elif unit_id == 4:
            sensor2 = BME280(p_mode=BME280_OSAMPLE_8)
            value = float(sensor2.read_pressure())

        elif unit_id == 2:
            sensor3 = BME280(h_mode=BME280_OSAMPLE_8)
            value = float(sensor3.read_humidity())
        else:
            error = 1

        return value, error


    def loop(self):
        while True:
            time.sleep(0.01)
            self.checkQueueForReadings()


if __name__ == "__main__":
    BME280I2C_ =  BME280I2C(sys.argv[1],sys.argv[2],sys.argv[3])
    BME280I2C_.loop()


