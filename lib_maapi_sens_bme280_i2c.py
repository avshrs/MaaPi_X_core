#!/usr/bin/python3.7
# -*- coding: utf-8 -*-import sys
###############################################################
#
#                          MAAPI X
#
##############################################################
from Adafruit_BME280 import *
from lib_maapi_sens_proto import SensProto

import time, copy, sys, os, signal

from datetime import datetime as dt
import subprocess

class BME280I2C(SensProto):
    def __init__(self,host,port,id_):
        self.id_                = id_
        self.objectname         = "BME_280"
        self.host               = host
        self.port               = int(port)
        self.timer_1            = dt.now()
        self.timer_2            = dt.now()
        super().__init__()

    def readValues(self, que, dev_id, devices_db, devices_db_rel):
        value = 0
        error = 0
        try:
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
    BME280I2C_ =  BME280I2C(sys.argv[1],sys.argv[2],sys.argv[3])
    BME280I2C_.loop()


