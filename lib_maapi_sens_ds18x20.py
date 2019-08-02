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

class DS18X20(SensProto):
    def __init__(self,host,port,id_, ss_proto):
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
        try:
            rom_id = devices_db[dev_id]["dev_rom_id"]
            if os.path.isfile(f'/sys/bus/w1/devices/{rom_id}/w1_slave'):
                w1_file = open(f'/sys/bus/w1/devices/{rom_id}/w1_slave','r')

                w1_crc = w1_file.readline().rsplit(' ', 1)
                w1_crc = w1_crc[1].replace('\n', '')
                self.maapilogger.log("DEBUG", f"CRC - {w1_crc}")
                if w1_crc == 'YES':
                    value = float(float((w1_file.readline()).rsplit('t=', 1)[1]) / float(1000))
                    self.maapilogger.log("DEBUG", f"Read_data_from_1w - Value is {value} for {rom_id} {dev_id}")
                    w1_file.close()
                else:
                    w1_file.close()
                    self.maapilogger.log("ERROR", "CRC False")
                    error = 2
            else:
                self.maapilogger.log("ERROR", f"ERROR reading values from {rom_id}: {dev_id} sensor not exist")

        except EnvironmentError as e:
            self.maapilogger.log("ERROR", f"throw : {e}")
            return value, 1
        else:
            return value, error

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
