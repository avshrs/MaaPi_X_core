#!/usr/bin/python3.7
# -*- coding: utf-8 -*-import sys
###############################################################
#
#                          MAAPI X
#
##############################################################

from lib_maapi_sens_proto import SensProto
import time, copy, sys, os, signal
from lim_maapi_i2c_bus import I2C_MaaPi
import smbus
from datetime import datetime as dt


class BME280I2C(SensProto):
    def __init__(self,host,port,id_):
        self.id_                = id_
        self.objectname         = "BH_1750"
        self.host               = host
        self.port               = int(port)
        self.maapiCommandLine   = []
        self.timer_1            = dt.now()
        self.timer_2            = dt.now()
        super().__init__()

    def readValues(self, que, dev_id, devices_db, devices_db_rel):
        value = 0
        error = 0
        try:
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
            #data = bus.read_i2c_block_data(DEVICE,ONE_TIME_HIGH_RES_MODE_1)

            bus = I2C_MaaPi(1)  # Rev 2 Pi uses 1
            data = bus.read_i2c_block_data(DEVICE, CONTINUOUS_HIGH_RES_MODE_1,32)
            data = bus.read_i2c_block_data(DEVICE, CONTINUOUS_HIGH_RES_MODE_1,32)
            value = (data[1] + (256 * data[0])) / 1.2



        except Exception as e:
            return value, 1
            self.maapilogger.log("ERROR", f"Exception read values {self.objectname}: {e}")
        else:
            return value, 0

    def loop(self):
        while True:
            time.sleep(0.1)
            self.checkQueueForReadings()
            self.responceToWatcher()

if __name__ == "__main__":
    BME280I2C_ =  BME280I2C(sys.argv[1],sys.argv[2],sys.argv[3])
    BME280I2C_.loop()








