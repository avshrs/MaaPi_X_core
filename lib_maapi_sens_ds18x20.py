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
import time, copy, sys, os, signal

from datetime import datetime as dt
import subprocess

class DS18X20():
    def __init__(self,host,port,id_):
        self.queue              = Queue.Queue()
        self.objectname         = "DS18X20"
        self.host               = host
        self.port               = int(port)
        self.maapiCommandLine   = []
        self.timer_1            = dt.now()
        self.timer_2            = dt.now()
        self.maapilogger        = MaapiLogger.Logger()
        self.maapilogger.name   = self.objectname
        self.readings           = Readings.Readings(self.objectname,self.host, self.port)
        self.maapiDB            = Db_connection.MaaPiDBConnection()
        self.socketServer       = SocketServer.SocketServer(self.objectname, self.queue, id_)
        self.socketServer.runTcpServer( self.host, self.port)

        self.pid                = os.getpid()

        self.selfkill           = False
        self.selfkillTime       = dt.now()
        signal.signal(signal.SIGTERM, self.service_shutdown)
        signal.signal(signal.SIGINT, self.service_shutdown)



    def service_shutdown(self, signum, frame):
        if not self.selfkill:
            self.maapilogger.log("STOP",f'Caught signal {signum} | stoping MaaPi {self.objectname}')
            self.selfkill = True
            self.selfkillTime = dt.now()

    def selfkilling(self):
        if self.selfkill and (dt.now() - self.selfkillTime).seconds >2:
            self.maapilogger.log("STOP",f'Reading modules Not Raise self term. - SocketServer not running self killing')
            raise SystemExit




    def updateCommandLine(self):
        self.maapiCommandLine = self.maapiDB.table("maapi_commandline").columns('cmd_update_rom_id', 'cmd_command').get()
        self.maapilogger.log("DEBUG","Update maapiCommandLine from database")

    def checkQueueForReadings(self):
        self.readings.checkQueueForReadings(self.readValues, self.queue)


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

    def loop(self):
        while True:
            if (dt.now() - self.timer_2).seconds >= 10:
                self.timer_2 = dt.now()
                self.updateCommandLine()
            time.sleep(0.01)
            self.checkQueueForReadings()
            self.selfkilling()

if __name__ == "__main__":
    DS18X20_ =  DS18X20(sys.argv[1],sys.argv[2],sys.argv[3] )
    DS18X20_.updateCommandLine()
    DS18X20_.loop()
