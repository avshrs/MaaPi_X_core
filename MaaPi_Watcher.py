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
        # vars

        self.selectorHost       = self.config.selectorHost
        self.selectorPort       = self.config.selectorPort
        self.watcherHost        = self.config.watcherHost
        self.watcherPort        = self.config.watcherPort
        self.selecorName        = self.config.selectorName
        self.thread             = []
        self.interpreterVer       ="/usr/bin/python{0}.{1}".format(sys.version_info[0],sys.version_info[1])
        self.lastResponce       = dt.now() - timedelta(hours = 1)

        self.socketServer       = SocketServer.SocketServer(self.objectname, self.watcherHost, self.watcherPort, self.queue, 1)
        self.socketServer.runTcpServer()

        self.selectorPid        = subprocess.Popen([self.interpreterVer, "MaaPi_Selector.py"])


    def __del__(self):
        self.maapilogger.log("DEBUG", "Joining tcp server thread ")


    def startSelectorModule(self):
        try:
            self.maapilogger.log("DEBUG", "Selector PID: {0}".format(self.selectorPid.pid))
            self.maapilogger.log("DEBUG", "Killing Selector - {pid}".format(pid=self.selectorPid.pid))
            self.selectorPid.kill()
        except Exception as e:
            self.maapilogger.log("ERROR", e)
        else:
            self.selectorPid = subprocess.Popen([self.interpreterVer, "MaaPi_Selector.py"])
            self.maapilogger.log("DEBUG", "Selector PID: {0}".format(self.selectorPid.pid))


    def checkSelector(self):
        try:
            if (dt.now() - self.lastResponce).seconds > 5:
                self.maapilogger.log("DEBUG", "Sending query to Selector: is ok? {0}, {1}".format(self.selectorHost, self.selectorPort))
                payload = self.helpers.pyloadToPicke(00, " ", self.watcherHost,self.watcherPort)
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


"""
id  name            type            decrtiption
------------------------------------------------------------------------
00  status          string - "ok"   recive status information

10  getReadings     list - id's     read data from sensor

20  putDataDB       dict id:value   put readings to dataBase
"""