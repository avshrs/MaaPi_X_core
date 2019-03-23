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
import time, copy, sys

from datetime import datetime as dt
import sys
import subprocess

class BME280I2C():
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


    def updateCommandLine(self):
        self.maapiCommandLine = self.maapiDB.table("maapi_commandline").columns('cmd_update_rom_id', 'cmd_command').get()
        self.maapilogger.log("DEBUG","Update maapiCommandLine from database")


    def checkQueueForReadings(self):
        self.readings.checkQueueForReadings(self.readValues, self.queue)


    def readValues(self, que, dev_id, devices_db, devices_db_rel):
        value = (subprocess.check_output(self.maapiCommandLine[f"{dev_id}"]['cmd_command'],shell=True,)).decode("utf-8")
        return float(value), 0

    def readValues(self, que, dev_id, devices_db, devices_db_rel):
        try:
            # 1 - temp
            # 2 - hum
            # 4 - press
            unit_id = devices_db[dev_id]['dev_unit_id']
            if name == 1:
                sensor = BME280(p_mode=BME280_OSAMPLE_8)
                temp = float(sensor.read_temperature())
                return temp, 0

            elif name == 4:
                sensor2 = BME280(p_mode=BME280_OSAMPLE_8)
                pressure = float(sensor2.read_pressure())
                return pressure, 0

            elif name == 2:
                sensor3 = BME280(h_mode=BME280_OSAMPLE_8)
                hum = float(sensor3.read_humidity())
                return hum, 0
        except:
            return 0, 1


    def loop(self):
        while True:
            if (dt.now() - self.timer_2).seconds >= 10:
                self.timer_2 = dt.now()
                self.updateCommandLine()
            time.sleep(0.01)
            self.checkQueueForReadings()


if __name__ == "__main__":
    BME280I2C_ =  BME280I2C(sys.argv[1],sys.argv[2],sys.argv[3])
    BME280I2C_.updateCommandLine()
    BME280I2C_.loop()


