#!/usr/bin/python3.7
# -*- coding: utf-8 -*-
##############################################################
#
#                          MAAPI 5.0
#                           Watcher
#
##############################################################

import pickle
import copy
import logging
import subprocess
import time
import os, sys
from datetime import datetime as dt
from datetime import timedelta
from threading import Lock, Thread
import lib_maapi_logger          as MaapiLogger
import lib_maapi_db_connection as Db_connection
import lib_maapi_queue as Queue
import lib_maapi_helpers as Helpers
import lib_maapi_socketClient as SocketClient
import lib_maapi_socketServer as SocketServer
import MaaPi_Config as Config


class MaapiWatcher():
    def __init__(self):
        # objects
        self.queue              = Queue.Queue()
        self.helpers            = Helpers.Helpers()
        self.config              = Config.MaapiVars()
        self.socketClient       = SocketClient.socketClient()
        self.socketServer       = SocketServer.SocketServer()
        self.maapiDB            = Db_connection.MaaPiDBConnection()
        self.maapilogger        = MaapiLogger.Logger()
        self.loopInterval       = 5
        # vars
        self.objectname         = "watcher"
        self.selectorHost       = self.config.selectorHost
        self.selectorPort       = self.config.selectorPort
        self.watcherHost        = self.config.watcherHost
        self.watcherPort        = self.config.watcherPort
        self.selecorName        = self.config.selectorName
        self.thread             = []
        self.interpreterVer       ="/usr/bin/python{0}.{1}".format(sys.version_info[0],sys.version_info[1])
        self.lastResponce       = dt.now() - timedelta(hours = 1)
        self.selectorPid        = subprocess.Popen([self.interpreterVer, "MaaPi_Selector.py"])

    def __del__(self):
        self.maapilogger.log(1, "Joining tcp server thread ")
        self.thread[0].join()


    def runTcpServerAsThreat(self):
            self.maapilogger.log(2, "Selector run tcp Server")
            self.thread.append(Thread(target=self.socketServer.startServer, args=(self.objectname, self.watcherHost, self.watcherPort, self.queue, 1)))
            self.thread[0].start()


    def startSelectorModule(self):
        try:
            self.maapilogger.log(1, self.selectorPid.pid)
            self.maapilogger.log(1, "Killing Selector - {pid}".format(pid=self.selectorPid.pid))
            self.selectorPid.kill()
        except Exception as e:
            self.maapilogger.log(1, e)
        else:
            self.selectorPid = subprocess.Popen([self.interpreterVer, "MaaPi_Selector.py"])
            self.maapilogger.log(1, self.selectorPid.pid)


    def checkSelector(self):
        try:
            if (dt.now() - self.lastResponce).seconds > 5:
                self.maapilogger.log(1, "Sending query to Selector: is ok? {0}, {1}".format(self.selectorHost, self.selectorPort))
                payload = self.helpers.pyloadToPicke(00, " ", self.watcherHost,self.watcherPort)
                recive =  self.socketClient.sendStrAndRecv(self.selectorHost, self.selectorPort, payload)
                if recive == bytes(0xff):
                    self.lastResponce = dt.now()
                    self.maapilogger.log(1, "Get responce from selector")
                else:
                    self.startSelectorModule()
        except Exception as e :
            self.maapilogger.log(1, "error: {exc}".format(exc = e))

    def loop(self):
        while True:
            time.sleep(self.loopInterval)
            self.checkSelector()

if __name__ == "__main__":
    MaapiSel =  MaapiWatcher()
    MaapiSel.runTcpServerAsThreat()
    MaapiSel.loop()


"""
id  name            type            decrtiption
------------------------------------------------------------------------
00  status          string - "ok"   recive status information

10  getReadings     list - id's     read data from sensor

20  putDataDB       dict id:value   put readings to dataBase
"""