#!/usr/bin/python3.7
# -*- coding: utf-8 -*-import sys
###############################################################
#
#                          MAAPI X
#
##############################################################

import time
import  sys
import  os
from w1thermsensor import W1ThermSensor as W1
from datetime import datetime as dt
from lib_maapi_sens_proto import SensProto


class DS18X20(SensProto):
    def __init__(self, host, port,id_, ss_proto):
        super().__init__()
        self.id_ = id_
        self.ssProto = ss_proto
        self.objectname = "DS18X20"
        self.host = host
        self.port = int(port)
        self.maapiCommandLine = []
        self.timer_1 = dt.now()
        self.timer_2 = dt.now()
        self.libInit()


    def readValues(self, que, dev_id, devices_db, devices_db_rel):
        error = 0
        value = 0
        rom_id = devices_db[dev_id]["dev_rom_id"]
        stype = {
            28:0x28,
            10:0x10,
            22:0x22,
            42:0x42
        }
        try: 
            value = W1(stype[int(rom_id[:2])], rom_id[3:]).get_temperature()
            return value, error
        except Exception as e:
            self.maapilogger.log("ERROR", f"ERROR reading values {rom_id}, {dev_id} sensor not exist")
            self.maapilogger.log("ERROR", f"Throw : {e}")
            return 85, 1

    def service_startup(self):
        pass

    def loop(self):
        while self.isRunning:
            time.sleep(0.01)
            self.checkQueueForReadings()
            self.responceToWatcher()


if __name__ == "__main__":
    DS18X20_ =  DS18X20(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])
    DS18X20_.service_startup()
    DS18X20_.loop()
