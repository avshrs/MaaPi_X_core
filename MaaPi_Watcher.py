#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
##############################################################
#
#                          MAAPI 5.0
#                           Watcher
#
##############################################################



import lib_maapi_socketServer               as SocketServer
import lib_maapi_queue                      as Queue
import lib_maapi_db_connection              as Db_connection
import lib_maapi_socketClient               as SocketClient
import MaaPi_Config                         as Config


from datetime import datetime as dt, timedelta
from threading import Lock, Thread
import subprocess
import logging
import time
import copy


class MaapiWatcher():
    def __init__(self):
        # objects
        self.queue              = Queue.queue()
        self.config             = Config.MaapiVars()
        self.socketClient       = SocketClient.socketClient()
        self.socketServer       = SocketServer.SocketServer()       
        self.maapiDB            = Db_connection.MaaPiDBConnection()

        # vars
        self.objectname         ="watcher"
        self.selectorHost       = self.config.selectorHost
        self.selectorPort       = self.config.selectorPort
        self.watcherHost        = self.config.watcherHost
        self.watcherPort        = self.config.watcherPort
        self.selecorName        = self.config.selectorName
        self.thread             = []

   
        self.lastResponce       = dt.now() - timedelta(hours=1)
        self.selectorPid        = subprocess.Popen(["/usr/bin/python3.4","MaaPi_Selector.py"])
        self.debug = 1
    
    def __del__(self):
        self._debug(1,"Joining tcp server thread ")
        self.thread[0].join()
    
    def _debug(self, level, msg):
        if self.debug >= level:
            print("DEBUG MaaPi Watcher\t\t{0} {1}, {2}".format(level, dt.now(), msg))


    def runTcpServerAsThreat(self):
            self._debug(2,"Selector run tcp Server")
            self.thread.append(Thread(target=self.socketServer.startServer, args=(self.objectname,self.watcherHost, self.watcherPort, self.queue, 1)))
            self.thread[0].start()


    def startSelectorModule(self):
        try:
            self._debug(1,"Killing Selector - {pid}".format(self.selectorPid))
            self.selectorPid.kill

        except Exception as e:
            self._debug(1,e)
        else:
            self.selectorPid = subprocess.Popen(["/usr/bin/python3.4","MaaPi_Selector.py"])
            self._debug(1,self.selectorPid.pid)
    
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
                    return "ok"          
                    del queue[self.objectname][self.selectorHost][self.selectorPort][que]
            return "nn"

   
    def checkSelector(self):
        try:
            if (dt.now() - self.lastResponce).seconds >5:
                self._debug(1,"self.checkSelector() sending ack ")
                responce = self.socketClient.sendStrAndRecv(self.selectorHost, self.selectorPort, "is ok?,{host},{port}".format(host=self.watcherHost,port=self.watcherPort))

                
                self._debug(1,"self.checkSelector() responce = |{responce}| ".format(responce=responce.data.decode("utf-8")))
                if responce.data.decode("utf-8") == "ok": 
                     self._debug(1,"ack from selector = ok") 
                     self.lastResponce = dt.now() 
                else: 
                     self._debug(1,"restart selector") 
                     self.startSelector()                              
        except:
             pass

    def loop(self):
        while True:
            time.sleep(5)
            self._debug(1,"self.checkSelector() ")
            self.checkSelector()
    
if __name__ == "__main__":
    MaapiSel =  MaapiWatcher()
    MaapiSel.runTcpServerAsThreat()
    MaapiSel.loop() 

