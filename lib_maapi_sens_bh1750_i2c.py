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

from lim_maapi_i2c_bus import I2C_MaaPi
import smbus

from datetime import datetime as dt
import sys
import subprocess

class BME280I2C():
    def __init__(self,host,port,id_):
        self.queue              = Queue.Queue()
        self.objectname         = "BH_1750"
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



    def checkQueueForReadings(self):
        self.readings.checkQueueForReadings(self.readValues, self.queue)


    def readValues(self, que, dev_id, devices_db, devices_db_rel):
        value = 0
        error = 0

        DEVICE = 0x23  # Default device I2C address
        POWER_DOWN = 0x00  # No active state
        POWER_ON = 0x01  # Power on
        RESET = 0x07  # Reset data register value
        # Start measurement at 4lx resolution. Time typically 16ms.
        CONTINUOUS_LOW_RES_MODE = 0x13
        # Start measurement at 1lx resolution. Time typically 120ms
        CONTINUOUS_HIGH_RES_MODE_1 = 0x10
        # Start measurement at 0.5lx resolution. Time typically 120ms
        CONTINUOUS_HIGH_RES_MODE_2 = 0x11
        # Start measurement at 1lx resolution. Time typically 120ms
        # Device is automatically set to Power Down after measurement.
        ONE_TIME_HIGH_RES_MODE_1 = 0x20
        # Start measurement at 0.5lx resolution. Time typically 120ms
        # Device is automatically set to Power Down after measurement.
        ONE_TIME_HIGH_RES_MODE_2 = 0x21
        # Start measurement at 1lx resolution. Time typically 120ms
        # Device is automatically set to Power Down after measurement.
        ONE_TIME_LOW_RES_MODE = 0x23

        #bus = smbus.SMBus(1) # Rev 1 Pi uses 0
        bus = I2C_MaaPi(1)  # Rev 2 Pi uses 1
        data = bus.write_byte(DEVICE, RESET)
        time.sleep(0.005)
        data = bus.read_i2c_block_data(DEVICE, CONTINUOUS_HIGH_RES_MODE_1,32)
        value = ((data[1] + (256 * data[0])) / 1.2)
        return value, error


    def loop(self):
        while True:
            time.sleep(0.01)
            self.checkQueueForReadings()

if __name__ == "__main__":
    BME280I2C_ =  BME280I2C(sys.argv[1],sys.argv[2],sys.argv[3])
    BME280I2C_.loop()








