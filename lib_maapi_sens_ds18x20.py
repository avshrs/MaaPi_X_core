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

from datetime import datetime as dt
import sys
import subprocess

class LinuxCmd():
    def __init__(self,host,port,id_):
        self.queue              = Queue.Queue()
        self.objectname         = "LinuxCmd"
        self.host               = host
        self.port               = port
        self.maapiCommandLine   = []
        self.timer_1            = dt.now()
        self.timer_2            = dt.now()
        self.maapilogger        = MaapiLogger.Logger()
        self.maapilogger.name   = self.objectname
        self.readings           = Readings.Readings(self.objectname,self.host, self.port)
        self.maapiDB            = Db_connection.MaaPiDBConnection()
        self.socketServer       = SocketServer.SocketServer(self.objectname, self.host, self.port, self.queue, id_)
        self.socketServer.runTcpServer()


    def updateCommandLine(self):
        self.maapiCommandLine = self.maapiDB.table("maapi_commandline").columns('cmd_update_rom_id', 'cmd_command').get()
        self.maapilogger.log("DEBUG","Update maapiCommandLine from database")


    def checkQueueForReadings(self):
        self.readings.checkQueueForReadings(self.readValues, self.queue)


    def readValues(self, que, dev_id, devices_db, devices_db_rel):
        rom_id = devices_db[dev_id]["dev_rom_id"]
        error = 0
        value = 0
        if os.path.isfile(f'/sys/bus/w1/devices/{rom_id}/w1_slave'):
            w1_file = open(f'/sys/bus/w1/devices/{rom_id}/w1_slave','r')
             self.maapilogger.log("DEBUG",f"Open file /sys/bus/w1/devices/{rom_id}/w1_slave")
            w1_line = w1_file.readline()
            w1_crc = w1_line.rsplit(' ', 1)
            w1_crc = w1_crc[1].replace('\n', '')
            if w1_crc == 'YES':
                 self.maapilogger.log("DEBUG", "CRC - YES")
                w1_line = w1_file.readline()
                w1_temp = w1_line.rsplit('t=', 1)
                value = float(float(w1_temp[1]) / float(1000))
                self._debug("DEBUG", f"Read_data_from_1w - Value is {temp} for rom_id[1] {dev_id}")
                w1_file.close()
                self.maapilogger.log("DEBUG", "Close file")
                error = 0
            else:
                w1_file.close()
                self.maapilogger.log("ERROR", "CRC False")
                error = 2
        else:
            error = 1
            self._debug("ERROR", f"ERROR reading values from rom_id[1]: {dev_id}")
        return value, error


    def loop(self):
        while True:
            if (dt.now() - self.timer_2).seconds >= 10:
                self.timer_2 = dt.now()
                self.updateCommandLine()
            time.sleep(0.01)
            self.checkQueueForReadings()


if __name__ == "__main__":
    LinuxCmd_ =  LinuxCmd(sys.argv[1],sys.argv[2],sys.argv[3] )
    LinuxCmd_.updateCommandLine()
    LinuxCmd_.loop()
