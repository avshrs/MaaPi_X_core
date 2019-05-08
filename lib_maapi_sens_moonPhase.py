#!/usr/bin/python3.7
# -*- coding: utf-8 -*-import sys
###############################################################
#
#                          MAAPI X
#
##############################################################

from lib_maapi_sens_proto import SensProto
import time, copy, sys, os, signal
from astral import *
from datetime import datetime as dt


class MoonPhase(SensProto):
    def __init__(self,host,port,id_):
        self.id_                = id_
        self.objectname         = "MoonPhase"
        self.host               = host
        self.port               = int(port)
        self.maapiCommandLine   = []
   
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
            time.sleep(0.1)
            self.checkQueueForReadings()

if __name__ == "__main__":
    MoonPhase_ =  MoonPhase(sys.argv[1],sys.argv[2],sys.argv[3] )
    MoonPhase_.loop()
