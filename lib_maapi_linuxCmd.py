
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
            queue = self.queue.getSocketRadings()
            queue_= queue[self.objectname][self.host][self.port]
            for que in queue_:
                if queue_[que][0] == self.helpers.instructions["readFromDev_id"]:
                    self.maapilogger.log("DEBUG",f"Device {queue_[que][1]} will be readed")
                    self.readValues(que, queue_[que][1], queue_[que][2])
        except Exception as e :
            self.maapilogger.log("ERROR",f"{e}")


    def readValues(self,que, dev_id, devices_db):
        try:
            self.maapilogger.log("DEBUG","Executing cmd and get results")
            value = (subprocess.check_output(self.maapiCommandLine[f"{dev_id}"]['cmd_command'],shell=True,)).decode("utf-8")

            self.maapilogger.log("INFO",f"Readed value {float(value)} nr:{que} cmd:{self.maapiCommandLine[str(dev_id)]['cmd_command']}  ")
            value, boolean = self.checkDev.checkDevCond( devices_db, dev_id, value)

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
