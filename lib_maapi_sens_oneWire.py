
#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
##############################################################
#
#                          MAAPI 5.0
#                           Selector
#
##############################################################


import lib_maapi_socketServer               as SocketServer
import lib_maapi_socketClient               as SocketClient
import lib_maapi_queue                      as Queue
import lib_maapi_db_connection              as Db_connection    
import MaaPi_Config                         as Config

from threading import Lock, Thread
from datetime import datetime as dt, timedelta

import time, os, copy



class MaapiSelector():

    def __init__(self):
        # objects
        self.queue              = Queue.queue()
        self.config             = Config.MaapiVars()
        self.sendstr            = SocketClient.socketClient()
        self.socketServer       = SocketServer.SocketServer()
        self.maapiDB            = Db_connection.MaaPiDBConnection()
        
        # vars
        self.board_id           = 0
        self.maapiLocation      = self.config.maapiLocation
        self.objectname         = "OneWireModule"
        self.selectorPort       = self.config.selectorPort
        self.selectorHost       = self.config.selectorHost
        self.thread             = []
        self.timer_1            = dt.now()
        self.debug = 1

        self._debug(1,"Initialising Selector Module ")
        
       
    def __del__(self):
        self._debug(1,"Joining tcp server thread ")
        self.thread[0].join()
     
    
    def _debug(self, level, msg):
        if self.debug >= level:
            print("DEBUG MaaPi Selector\t\t{0} {1}, {2}".format(level, dt.now(), msg))

    
    def runTcpServer(self):
            self._debug(2,"Selector run tcp Server")
            self.thread.append(Thread(target=self.socketServer.startServer, args=(self.objectname,self.selectorHost, self.selectorPort, self.queue, 1)))
            self.thread[0].start()

    def scanQueueForSelectorAck(self,queue):
        try:
            if queue[self.objectname][self.selectorHost][self.selectorPort]:    
                queue__ = copy.deepcopy(queue[self.objectname][self.selectorHost][self.selectorPort])
        except:
            pass
        else:
            for que in queue__:
                data     = queue__[que][0]
                recvHost = queue__[que][1]
                recvPort = queue__[que][2]
                dtime    = queue__[que][3]
                self._debug(1,data)
                if data == "ok":                  
                    self._debug(1,"get ok from selector")
                          
                    del queue[self.objectname][self.selectorHost][self.selectorPort][que]
            return "nn"

   

    def read_data_from_1w(self, rom_id, dev_id):
        if os.path.isfile('/sys/bus/w1/devices/{0}/w1_slave'.format(rom_id)):
            w1_file = open('/sys/bus/w1/devices/{0}/w1_slave'.format(rom_id),'r')
            self._debug(1,"Open file /sys/bus/w1/devices/{0}/w1_slave".format(rom_id))
            w1_line = w1_file.readline()
            w1_crc = w1_line.rsplit(' ', 1)
            w1_crc = w1_crc[1].replace('\n', '')
            if w1_crc == 'YES':
                self._debug(2, "CRC - YES")
                w1_temp = w1_file.readline().rsplit('t=', 1)
                temp = float(float(w1_temp[1]) / float(1000))
                self._debug(1, "Read_data_from_1w - Value is {0} for rom_id[1] {1}".format(temp, dev_id))
                w1_file.close()
                return temp
            else:
                return "CRC_NO"
        else:
            return "FILE_NOT_EXIST"

    

    def SendDataToServer(self,host,port,data):
        try:
            self.sendstr.sendStr(host, port, data)
        except Exception as e:
            self._debug(1,"Exception - SendDataToServer {Ex}".format(Ex=e))


    def loop(self): 
        while True:
            if (dt.now() - self.timer_1).seconds >1:
                self.DeviceList()
                self.timer1 = dt.now()
            time.sleep(0.01)
            self.scanQueueForIncommingQuerys(self.queue.getSocketRadings())
    
if __name__ == "__main__":
    MaapiSel =  MaapiSelector()
    MaapiSel.runTcpServer()
    MaapiSel.loop() 

def __init__(self, *args):
        for rom_id in args:
            condition, condition_min_max, force_value = Check().condition(
                rom_id[0])
            self._debug(
                1,
                "Condition is = {0}\t condition_min_max is = {1}, \t forced value is = {2}".
                format(condition, condition_min_max, force_value))
            if condition:
                if condition_min_max:
                    self.read_data_from_1w(rom_id[1], rom_id[0])
                    

                else:

                    maapidb.MaaPiDBConnection.insert_data(
                        rom_id[0], force_value, ' ', True)
                    self._debug(
                        1,
                        "Forcing value for sensor id = {0} \tforced vslur is = {1} ".
                        format(rom_id[0], force_value))
            else:
                self.read_data_from_1w(rom_id[1], rom_id[0])