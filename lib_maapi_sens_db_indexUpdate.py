#!/usr/bin/python3.6
# -*- coding: utf-8 -*-import sys
###############################################################
#
#                          MAAPI X
#
##############################################################

from lib_maapi_sens_proto import SensProto
import time, copy, sys, os, signal

from datetime import datetime as dt


class MoonPhase(SensProto):
    def __init__(self,host,port,id_, ss_proto):
        super().__init__()
        self.id_ = id_
        self.ssProto = ss_proto
        self.objectname = "DB_Index"
        self.host = host
        self.port = int(port)
        self.maapiCommandLine = []
        self.libInit()

    def readValues(self, que, dev_id, devices_db, devices_db_rel):
        value, error = 0, 0
        # try:
        self.maapiDB.reindexTable(devices_db)

        # except Exception as e:
        #     return 0, 1
        #     self.maapilogger.log("ERROR", f"Exception read values {self.objectname}: {e}")
        # else:
        return 1, 0

    def loop(self):
        while True:
            time.sleep(0.1)
            self.checkQueueForReadings()
            self.responceToWatcher()


if __name__ == "__main__":
    MoonPhase_ =  MoonPhase(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])
    MoonPhase_.loop()
