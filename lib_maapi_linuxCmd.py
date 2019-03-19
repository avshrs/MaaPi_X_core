
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
import time, copy, sys

from datetime import datetime as dt
import sys
import subprocess

class LinuxCmd():
    def __init__(self,host,port,id_):
        self.queue              = Queue.Queue()
        self.helpers            = Helpers.Helpers()
        self.checkDev           = CheckDev.CheckDevCond()
        self.objectname         = "LinuxCmd"
        self.host               = host
        self.port               = port
        self.maapiCommandLine   = []
        self.timer_1            = dt.now()
        self.timer_2            = dt.now()
        self.maapilogger        = MaapiLogger.Logger()
        self.maapilogger.name   = self.objectname
        self.maapiDB            = Db_connection.MaaPiDBConnection()
        self.socketServer       = SocketServer.SocketServer(self.objectname, self.host, self.port, self.queue, id_)
        self.socketServer.runTcpServer()


    def updateCommandLine(self):
        self.maapiCommandLine = self.maapiDB.table("maapi_commandline").columns('cmd_update_rom_id', 'cmd_command').get()
        self.maapilogger.log("DEBUG","Update maapiCommandLine from database")


    def checkQueueForReadings(self):
        try:
            queue  = self.queue.getSocketRadings()
            queue_ = queue[self.objectname][self.host][self.port]
            for nr in queue_:
                dev_id          = queue_[nr][1]
                devices_db      = queue_[nr][2]
                devices_db_rel  = queue_[nr][3]
                if queue_[nr][0] == self.helpers.instructions["readFromDev_id"]:
                    self.maapilogger.log("DEBUG",f"Device {dev_id} will be readed")
                    try:
                        value, error = self.readValues(nr, dev_id, devices_db)
                        self.maapilogger.log("INFO",f"Readed id: {nr} \tDevID: {dev_id} \tName: {devices_db[dev_id]['dev_user_name']} \tValue: {float(value)} ")
                    except Exception as e:
                        value = 0
                        error = 2
                        self.maapilogger.log("ERROR",f"Error while reading values: {e}")
                    self.insertReadingsToDB(nr ,value, dev_id, devices_db, devices_db_rel, error)
        except Exception as e :
            self.maapilogger.log("ERROR",f"{e}")


    def readValues(self, que, dev_id, devices_db):
        value = (subprocess.check_output(self.maapiCommandLine[f"{dev_id}"]['cmd_command'],shell=True,)).decode("utf-8")
        return value, 0


    def insertReadingsToDB(self, nr, readed_value, dev_id, devices_db, devices_db_rel,  error_code):
        try:
            if error_code > 0:
                #9999.0 reading ok
                #9999.1 device not exist
                #9999.2 error while reading
                self.maapilogger.log("DEBUG","Error while reading ")
                self.maapiDB.insert_readings(dev_id,float(f"9999.{error_code}"," ",False))
            else:
                value, boolean = self.checkDev.checkDevCond( devices_db, devices_db_rel, dev_id, readed_value)
                self.maapilogger.log("DEBUG","Insert readings to DataBase")
                self.maapiDB.insert_readings(dev_id,value," ",boolean)
        except EnvironmentError as e:
            self.maapilogger.log("ERROR",f"Error reading data from CMD: {e}")
            self.maapiDB.insert_readings(dev_id,0," ",False)


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
