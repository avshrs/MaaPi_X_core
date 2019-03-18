
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
            queue_= copy.deepcopy(queue[self.objectname][self.host][self.port])

        except Exception as e :
            self.maapilogger.log("DEBUG",f"{e}")
        else:
            for que in queue_:
                if queue_[que][0] == self.helpers.instructions["readFromDev_id"]:
                    self.readValues(data["dev_id"])
                    del queue[self.objectname][self.host][self.port][que]
                    self.maapilogger.log("INFO","Value Readed From {0} - Entry Deletet From Queue".format(data["dev_id"]))
                self.maapilogger.log("DEBUG",f"Reading queue id={id_} data={queue_[que][2]['dev_id']} recvHost={queue_[que][2]} recvPort={queue_[que][3]}")

    def readValues(self, dev_id):
        try:
            self.maapilogger.log("DEBUG","Executing cmd and get results")
            value = (subprocess.check_output(self.maapiCommandLine[f"{dev_id}"]['cmd_command'],shell=True,)).decode("utf-8")
            self.maapilogger.log("DEBUG",self.maapiCommandLine[f"{dev_id}"]['cmd_command'])
            self.maapilogger.log("DEBUG",f"Readed value {value}")
            self.maapiDB.insert_readings(dev_id,value," ",True)
        except EnvironmentError as e:
            self.maapilogger.log("ERROR",f"Error reading data from CMD: {e}")
            self.maapiDB.insert_readings(dev_id,0," ",False)

    def loop(self):
        while True:
            if (dt.now() - self.timer_2).seconds >= 60:
                self.updateCommandLine()
                self.timer_2 = dt.now()
            time.sleep(0.05)
            self.checkQueueForReadings()


if __name__ == "__main__":

    LinuxCmd_ =  LinuxCmd(sys.argv[1],sys.argv[2],sys.argv[3] )
    LinuxCmd_.updateCommandLine()
    LinuxCmd_.loop()


def read_data_from_1w(self, rom_id, dev_id):
        if os.path.isfile('/sys/bus/w1/devices/{0}/w1_slave'.format(rom_id)):
            w1_file = open('/sys/bus/w1/devices/{0}/w1_slave'.format(rom_id),'r')
            self._debug(1,
                        "Open file /sys/bus/w1/devices/{0}/w1_slave"
                        .format(rom_id))
            w1_line = w1_file.readline()
            w1_crc = w1_line.rsplit(' ', 1)
            w1_crc = w1_crc[1].replace('\n', '')
            if w1_crc == 'YES':
                self._debug(2, "CRC - YES")
                w1_line = w1_file.readline()
                w1_temp = w1_line.rsplit('t=', 1)
                temp = float(float(w1_temp[1]) / float(1000))
                self._debug(
                    1, "Read_data_from_1w - Value is {0} for rom_id[1] {1}".
                    format(temp, dev_id))
                w1_file.close()
                self._debug(2, "Close file")
                maapidb.MaaPiDBConnection.insert_data(
                    dev_id, temp, ' ', True)
            else:
                w1_file.close()
                self._debug(2, "CRC False")
                maapidb.MaaPiDBConnection.insert_data(dev_id, 99999, ' ',
                                                      False)
        else:
            self._debug(
                1, "\tERROR reading values from rom_id[1]: {0}".format(dev_id))
            maapidb.MaaPiDBConnection.insert_data(dev_id, 99999, ' ', False)
