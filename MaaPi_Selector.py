
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
import time

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
        self.objectname         = "selector"
        self.selectorPort       = self.config.selectorPort
        self.selectorHost       = self.config.selectorHost
        self.thread             = []
        self.timer1             = dt.now()

    
    def runTcpServer(self):
        print ("run server")
        self.thread.append(Thread(target=self.socketServer.startServer, args=(self.objectname,self.selectorHost, self.selectorPort, self.queue, 1)))
        print ("start server")
        self.thread[0].start()
    

    def checkDbForOldreadings(self):
        readings = [1,2,3]
        return readings

    
    def scanTcpIncommingQuerys(self,queue):
        try:
            if queue[self.objectname][self.selectorHost][self.selectorPort]:    
                for que in queue[self.objectname][self.selectorHost][self.selectorPort]:
                    data     = (queue[self.objectname][self.selectorHost][self.selectorPort][que][0].decode("utf-8"))
                    recvHost = (queue[self.objectname][self.selectorHost][self.selectorPort][que][1])
                    recvPort = (queue[self.objectname][self.selectorHost][self.selectorPort][que][2])
                    dtime    = (queue[self.objectname][self.selectorHost][self.selectorPort][que][3])
                    
                    if data == "is ok?":
                        print (dtime + " resonce sended")
                        self.SendDataToServer(recvHost,recvPort,"ok")
                    
                    del queue[self.objectname][self.selectorHost][self.selectorPort][que]
        except:
            pass

    def DeviceList(self):
        board_location = self.maapiDB.table("maapi_machine_locations").filters_eq(ml_enabled=True).get()
        for i in board_location:
            if board_location[i]["ml_location"] == self.maapiLocation:
                self.board_id = board_location[i]["id"]
        
        data = self.maapiDB.table("devices").columns(
                "dev_id",
                "dev_type_id",
                "dev_rom_id",
                "dev_bus_type_id",
                "dev_last_update",
                "dev_interval",
                "dev_interval_unit_id",
                "dev_interval_queue",
                "dev_machine_location_id",
                ).order_by('dev_id').filters_eq(
                dev_status=True, dev_machine_location_id=self.board_id).get()
        print(data)
 

    def SendDataToServer(self,host,port,data):
        try:
            self.sendstr.sendStr(host, port, data)
        except Exception as e:
            print (e)


    def loop(self):
        
        while True:
            if (dt.now() - self.timer1).seconds >1:
                print (1)
                self.DeviceList()
                self.timer1 = dt.now()
            time.sleep(0.01)
            
          #  print ("{0} - pause - Selector".format(dt.now()))
            #self.scanTcpIncommingQuerys(self.queue.get_tcp_radings())
            self.scanTcpIncommingQuerys(self.queue.getSocketRadings())
    
if __name__ == "__main__":
    MaapiSel =  MaapiSelector()
    MaapiSel.runTcpServer()
    MaapiSel.loop() 

