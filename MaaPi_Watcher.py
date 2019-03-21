#!/usr/bin/python3.7
# -*- coding: utf-8 -*-import sys
###############################################################
#
#                          MAAPI X
#
##############################################################
import copy
import logging
import subprocess
import time
import os, sys
from datetime import datetime as dt
from datetime import timedelta
from threading import Lock, Thread

import lib_maapi_main_logger        as MaapiLogger
import lib_maapi_main_dbORM         as Db_connection
import lib_maapi_main_queue         as Queue
import lib_maapi_main_helpers       as Helpers
import lib_maapi_main_socketClient  as SocketClient
import lib_maapi_main_socketServer  as SocketServer
import MaaPi_Config                 as Config


class MaapiWatcher():
    def __init__(self):
        self.objectname         = "Watcher"
        # objects
        self.queue              = Queue.Queue()
        self.helpers            = Helpers.Helpers()
        self.config              = Config.MaapiVars()
        self.socketClient       = SocketClient.socketClient()
        self.maapiDB            = Db_connection.MaaPiDBConnection()
        self.maapilogger        = MaapiLogger.Logger()
        self.maapilogger.name   = self.objectname
        self.loopInterval       = 5
        self.selectorHost       = self.config.selectorHost
        self.selectorPort       = self.config.selectorPort
        self.watcherHost        = self.config.watcherHost
        self.watcherPort        = self.config.watcherPort
        self.selecorName        = self.config.selectorName
        self.thread             = []
        self.interpreterVer       =f"{sys.executable}"
        self.lastResponce       = dt.now() - timedelta(hours = 1)
        self.socketServer       = SocketServer.SocketServer(self.objectname, self.queue, 1)
        self.socketServer.runTcpServer(self.watcherHost, self.watcherPort)
        self.selectorPid        = subprocess.Popen([self.interpreterVer, "MaaPi_Selector.py"])


    def startSelectorModule(self):
        try:
            self.maapilogger.log("DEBUG", f"Killing Selector - {self.selectorPid.pid}")
            self.selectorPid.kill()
        except Exception as e:
            self.maapilogger.log("ERROR", e)
        else:
            self.selectorPid = subprocess.Popen([self.interpreterVer, "MaaPi_Selector.py"])
            self.maapilogger.log("DEBUG", f"Selector PID: {self.selectorPid.pid}")


    def checkSelector(self):
        try:
            if (dt.now() - self.lastResponce).seconds > 5:
                self.maapilogger.log("DEBUG", f"Sending query to Selector: is ok? {self.selectorHost}, {self.selectorPort}")
                payload = self.helpers.pyloadToPicke(00, " ", " ", " ", self.watcherHost,self.watcherPort)
                recive =  self.socketClient.sendStrAndRecv(self.selectorHost, self.selectorPort, payload)
                if recive == bytes(0xff):
                    self.lastResponce = dt.now()
                    self.maapilogger.log("DEBUG", "Get responce from selector")
                else:
                    self.startSelectorModule()
        except Exception as e :
            self.maapilogger.log("ERROR", "error: {exc}".format(exc = e))

    def loop(self):
        while True:
            time.sleep(self.loopInterval)
            self.checkSelector()

if __name__ == "__main__":
    MaapiSel =  MaapiWatcher()
    MaapiSel.loop()