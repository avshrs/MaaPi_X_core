
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
import time, copy


from datetime import datetime as dt
import sys
import subprocess


class LinuxCmd():
    def __init__(self,host,port,id):
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
        self.socketServer       = SocketServer.SocketServer(self.objectname, self.host, self.port, self.queue, 1)
        self.socketServer.runTcpServer()


    def updateCommandLine(self):
        self.maapiCommandLine = self.maapiDB.table("maapi_commandline").columns('cmd_update_rom_id', 'cmd_command').get()
        self.maapilogger.log("DEBUG","Update maapiCommandLine from database")


    def checkQueueForReadings(self):
        try:
            queue_= copy.deepcopy(queue[self.objectname][self.host][self.port])
        except:
            pass
        else:
            for que in queue__:
                id_       = queue_[que][0]
                data_     = queue_[que][1]
                recvHost_ = queue_[que][2]
                recvPort_ = queue_[que][3]
                dtime_    = queue_[que][4]
                if id_ == self.instructions["readFromDev_id"]:
                    del queue[self.objectname][self.host][selectorPort][self.port]


    def readValues(self, data, id):
        try:
            self.maapilogger.log("DEBUG","Executing cmd and get results")
            value = subprocess.check_output(maapi_commandline[str(arg[0])]['cmd_command'],shell=True,)
            maapiDB.insert_data(arg[0], float(value[1]), arg[2], True)
        except:
            self.maapilogger.log("ERROR","Error reading data from CMD")
            maapiDB.insert_data(arg[0], 0, arg[2], False)

    def loop(self):
        while True:
            if (dt.now() - self.timer_2).seconds >= 60:
                self.updateCommandLine()
                self.timer_2 = dt.now()
            time.sleep(0.1)
            self.checkQueueForReadings()


if __name__ == "__main__":

    LinuxCmd_ =  LinuxCmd(sys.argv[1],sys.argv[2],sys.argv[3] )
    LinuxCmd_.updateCommandLine()
    LinuxCmd_.loop()
