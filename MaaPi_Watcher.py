#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
##############################################################
#
#                          MAAPI 5.0
#                           Watcher
#
##############################################################



import lib_maapi_watcherSocketServer        as WatcherSocketServer 
import lib_maapi_queue                      as Queue
import lib_maapi_db_connection              as Db_connection
import lib_maapi_socketClient               as SocketClient
import MaaPi_Config                         as Config

from datetime import datetime as dt, timedelta
from threading import Lock, Thread
import subprocess
import logging
import time



class MaapiWatcher():
    def __init__(self):
        # objects
        self.queue              = Queue.queue()
        self.config             = Config.MaapiVars()
        self.socketClient       = SocketClient.socketClient()
        self.socketServer       = WatcherSocketServer.WatcherSocketServer()
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

        print (self.selectorPid.pid)
        print(self.queue)
    
    
    def _debug(self, level, msg):
        if self.debug >= level:
            print("DEBUG MaaPi Connection DB Main {0} {1}, {2}".format(level, dt.now(), msg))


    def runTcpServer(self):
        print ("run server")
        self.thread.append(Thread(target=self.socketServer.startServer, args=(self.watcherHost, self.watcherPort, self.queue, 0)))
        print ("start server")
        self.thread[0].start()
    

    def startSelector(self):
        try:
            self.selectorPid.kill
        except Exception as e:
            print(e)
        else:
            self.selectorPid = subprocess.Popen(["/usr/bin/python3.4","MaaPi_Selector.py"])
            print (self.selectorPid.pid)
    
 
    
    def checkSelector(self):
        try:
            
            if (dt.now() - self.lastResponce).seconds >5:
                print ("is ok?")
                responce = self.socketClient.sendStr(self.selectorHost, self.selectorPort, "is ok?" )
                if responce.decode("utf-8") == "ok":
                    print ("ok")
                    self.lastResponce = dt.now()
                else:
                    print ("restart selector")
                    self.startSelector()

        except Exception as e:
            print (e)
            print ("something goes wrong  -start selector")
            self.startSelector()
             
                 


    def loop(self):
        while True:
            time.sleep(5)
            
            print ("{0} - pause - Watcher".format(dt.now()))
            self.checkSelector()
    
if __name__ == "__main__":
    MaapiSel =  MaapiWatcher()
    MaapiSel.runTcpServer()
    MaapiSel.loop() 

