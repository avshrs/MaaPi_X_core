
#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
##############################################################
#
#                          MAAPI 5.0
#                           Selector
#
##############################################################

import lib_checkDeviceCond                  as CheckDev
import lib_maapi_queue                      as Queue
import lib_maapi_logger                     as MaapiLogger
import lib_maapi_socketClient               as SocketClient
import lib_maapi_socketServer               as SocketServer
import lib_maapi_helpers                    as Helpers
import lib_maapi_db_connection              as Db_connection
import lib_maapi_readings                   as Readings
import time, copy, sys


from datetime import datetime as dt
import sys
import subprocess


class MaaPiMath():
    def __init__(self,host,port,id_):
        self.queue              = Queue.Queue()
        self.objectname         = "MaaPiMath"
        self.host               = host
        self.port               = port
        self.maapiMathTable     = []
        self.timer_1            = dt.now()
        self.timer_2            = dt.now()
        self.maapilogger        = MaapiLogger.Logger()
        self.maapilogger.name   = self.objectname
        self.maapiDB            = Db_connection.MaaPiDBConnection()
        self.readings           = Readings.Readings(self.objectname,self.host, self.port)
        self.socketServer       = SocketServer.SocketServer(self.objectname, self.host, self.port, self.queue, id_)
        self.socketServer.runTcpServer()


    def updateMathTable(self):
        self.maapiMathTable = self.maapiDB.table("maapi_math").columns( 'id',
                                                                        'math_user_id',
                                                                        'math_name',
                                                                        'math_update_rom_id',
                                                                        'math_data_from_1_id',
                                                                        'math_data_from_2_id',
                                                                        'math_data_from_3_id',
                                                                        'math_data_from_4_id',
                                                                        'math_math',
                                                                        'math_descript',
                                                                        'math_enabled',
                                                                        ).get()
        self.maapilogger.log("DEBUG","Update maapiMathTable from database")


    def checkQueueForReadings(self):
        self.readings.checkQueueForReadings(self.readValues, self.queue)


    def readValues(self, nr, dev_id, devices_db, devices_db_rel):
        value = 0
        error = True
        for math_id in self.maapiMathTable:
            if int(self.maapiMathTable[math_id]["math_update_rom_id"]) == dev_id:
                value = 0
                error = 0
                if self.maapiMathTable[math_id]['math_data_from_1_id']:

                    V1 = v1 = devices_db_rel[int(self.maapiMathTable[math_id]['math_data_from_1_id'])]['dev_value']
                else: V1 = v1 = 'none'

                if self.maapiMathTable[math_id]['math_data_from_2_id']:
                    V2 = v2 = devices_db_rel[int(self.maapiMathTable[math_id]['math_data_from_2_id'])]['dev_value']
                else: V2 = v2 = 'none'

                if self.maapiMathTable[math_id]['math_data_from_3_id']:
                    V3 = v3 = devices_db_rel[int(self.maapiMathTable[math_id]['math_data_from_3_id'])]['dev_value']
                else: V3 = v3 = 'none'

                if self.maapiMathTable[math_id]['math_data_from_4_id']:
                    V4 = v4 = devices_db_rel[int(self.maapiMathTable[math_id]['math_data_from_4_id'])]['dev_value']
                else: V4 = v4 = 'none'

                value = eval(self.maapiMathTable[math_id]["math_math"])

                self.maapilogger.log("DEBUG",f"Readed value {float(value)} nr:{nr}")
            else:
                self.maapilogger.log("DEBUG",f"Device Not exist in list {dev_id}")
        return value, error


    def loop(self):
        while True:
            if (dt.now() - self.timer_2).seconds >= 10:
                self.timer_2 = dt.now()
                self.updateMathTable()
            time.sleep(0.01)
            self.checkQueueForReadings()


if __name__ == "__main__":
    MaaPiMath_ =  MaaPiMath(sys.argv[1], sys.argv[2], sys.argv[3])
    MaaPiMath_.updateMathTable()
    MaaPiMath_.loop()
