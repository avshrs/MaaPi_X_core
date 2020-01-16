#!/usr/bin/python3.7
# -*- coding: utf-8 -*-import sys
###############################################################
#
#                          MAAPI X
#
##############################################################
from Libs.integra import Integra

from lib_maapi_sens_proto import SensProto
import time, copy, sys, os, signal
from datetime import datetime as dt

class INTEGRA(SensProto):
    def __init__(self,host,port,id_, ss_proto):
        super().__init__()
        self.id_ = id_
        self.ssProto = ss_proto
        self.objectname = "INTEGRA"
        self.host = host
        self.port = int(port)
        self.maapiCommandLine = []
        self.timer_1 = dt.now()
        self.timer_2 = dt.now()
        self.libInit()
        self.integ = Integra(user_code=1234, host='192.168.1.240', port=25197)
        self.inputs = []
        self.outputs = []
        self.in_table = {}
        self.out_table = {}
        self.interval = 10

    def readValues(self, que, dev_id, devices_db, devices_db_rel):
        error = 0
        value = 0
        self.maapilogger.log("ERROR", "before try")
        try:
            pin = devices_db[dev_id]["dev_gpio_pin"]
            rom_id = devices_db[dev_id]["dev_rom_id"]
            self.maapilogger.log("ERROR", "in try")
            if rom_id[-2:] == "in":
                self.maapilogger.log("ERROR", "in if in")
                if pin in self.in_table and (dt.now() - self.in_table[i]).seconds <= self.interval:
                    self.maapilogger.log("ERROR", "set value =1")
                    value = 1
            else:
                if pin in self.out_table and (dt.now() - self.out_table[i]).seconds <= self.interval:
                    value = 1
            return value, error
        except EnvironmentError as e:
            self.maapilogger.log("ERROR", f"throw : {e}")
            return 9999, 1
        

    def service_startup(self):
        pass 

    def getreadings(self):
        try:
            self.inputs = self.integ.get_violated_zones()
            for i in self.inputs:
                if i not in self.in_table:
                    self.in_table[i] = dt.now()
                elif (dt.now() - self.in_table[i]).seconds >= self.interval:
                    self.in_table[i] = dt.now()
            self.inputs = []
            self.outputs = self.integ.get_active_outputs()
            for i in self.outputs:
                if i not in self.out_table:
                    self.out_table[i] = dt.now()
                elif (dt.now() - self.out_table[i]).seconds >= self.interval:
                    self.out_table[i] = dt.now()
            self.outputs = []
            
        except Exception as e:
            self.maapilogger.log("ERROR", f"throw : {e}")
    def loop(self):
        while self.isRunning:
            time.sleep(0.1)
            self.getreadings()
            self.checkQueueForReadings()
            self.responceToWatcher()


if __name__ == "__main__":
    DS18X20_ =  INTEGRA(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])
    DS18X20_.service_startup()
    DS18X20_.loop()
