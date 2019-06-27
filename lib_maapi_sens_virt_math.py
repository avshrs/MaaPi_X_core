#!/usr/bin/python3.7
# -*- coding: utf-8 -*-import sys
###############################################################
#
#                          MAAPI X
#
##############################################################

from lib_maapi_sens_proto import SensProto
import time, copy, sys, os, signal
import numpy as np
from datetime import datetime as dt


class MaaPiMath(SensProto):
    def __init__(self, host, port, id_):
        super().__init__()
        self.objectname = "MaaPiMath"
        self.id_ = id_
        self.host = host
        self.port = int(port)
        self.maapiMathTable = []
        self.timer_1 = dt.now()
        self.libInit()


    def updateMathTable(self):
        try:
            self.maapiMathTable = self.maapiDB.table(
                "maapi_math").columns(
                    'id',
                    'math_user_id',
                    'math_name',
                    'math_update_rom_id',

                    'math_data_from_1_id',
                    'math_data_from_1_date',
                    'math_data_from_1_count',

                    'math_data_from_2_id',
                    'math_data_from_2_date',
                    'math_data_from_2_count',

                    'math_data_from_3_id',
                    'math_data_from_3_date',
                    'math_data_from_3_count',

                    'math_data_from_4_id',
                    'math_data_from_4_date',
                    'math_data_from_4_count',

                    'math_math',
                    'math_descript',
                    'math_enabled',
                    ).get()
            self.maapilogger.log("DEBUG", "Update maapiMathTable from database")
        except:
            pass

    def getDataHistory(self, dev_id, nr, math_id, devices_db_rel):
        try:
            del deta
        except:
            pass
        if self.maapiMathTable[math_id][f'math_data_from_{nr}_count']:
            if self.maapiMathTable[math_id][f'math_data_from_{nr}_count'] > 0:
                data = self.maapiDB.select_last_nr_of_values(dev_id, self.maapiMathTable[math_id][f'math_data_from_{nr}_count'])

        elif self.maapiMathTable[math_id][f'math_data_from_{nr}_date']:
            if self.maapiMathTable[math_id][f'math_data_from_{nr}_date'] > 0:
                data = self.maapiDB.select_last_timeRange_of_values(dev_id, self.maapiMathTable[math_id][f'math_data_from_{nr}_date'])
        else:
            data = devices_db_rel[float(self.maapiMathTable[math_id][f'math_data_from_{nr}_id'])]['dev_value']
        return data

    def readValues(self, nr, dev_id, devices_db, devices_db_rel):
        value = 0
        error = 0
        try:
            for math_id in self.maapiMathTable:
                if int(self.maapiMathTable[math_id]["math_update_rom_id"]) == dev_id:

                    if self.maapiMathTable[math_id]['math_data_from_1_id']:
                        V1 = v1 = self.getDataHistory(self.maapiMathTable[math_id]['math_data_from_1_id'], 1, math_id, devices_db_rel)
                    else: V1 = v1 = 'none'

                    if self.maapiMathTable[math_id]['math_data_from_2_id']:
                        V2 = v2 = self.getDataHistory(self.maapiMathTable[math_id]['math_data_from_2_id'], 2, math_id, devices_db_rel)
                    else: V2 = v2 = 'none'

                    if self.maapiMathTable[math_id]['math_data_from_3_id']:
                        V3 = v3 = self.getDataHistory(self.maapiMathTable[math_id]['math_data_from_3_id'], 3, math_id, devices_db_rel)
                    else: V3 = v3 = 'none'

                    if self.maapiMathTable[math_id]['math_data_from_4_id']:
                        V4 = v4 = self.getDataHistory(self.maapiMathTable[math_id]['math_data_from_4_id'], 4, math_id, devices_db_rel)
                    else: V4 = v4 = 'none'

                    value = eval(self.maapiMathTable[math_id]["math_math"])
                    self.maapilogger.log("DEBUG",f"Readed value {float(value)} nr:{nr}")
                else:
                    self.maapilogger.log("DEBUG",f"Device Not exist in list {dev_id}")
        except EnvironmentError as e:
            self.maapilogger.log("ERROR", f"Exception read values {self.objectname}: {e}")
            return value, 1
        else:
            return value, error

    def service_startup(self):
        self.updateMathTable()


    def loop(self):
        while self.isRunning:
            if (dt.now() - self.timer_1).seconds >= 10:
                self.timer_1 = dt.now()
                self.updateMathTable()
            time.sleep(0.01)
            self.responceToWatcher()
            self.checkQueueForReadings()


if __name__ == "__main__":
    MaaPiMath_ =  MaaPiMath(sys.argv[1], sys.argv[2], sys.argv[3])
    MaaPiMath_.service_startup()
    MaaPiMath_.loop()
