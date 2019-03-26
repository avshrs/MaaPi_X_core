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
import os, sys, signal
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
        self.interpreterVer       =f"{sys.executable}"
        self.lastResponce       = dt.now() - timedelta(hours = 1)
        self.socketServer       = SocketServer.SocketServer(self.objectname, self.queue, 1)
        self.selectorPid        = subprocess.Popen([self.interpreterVer, "MaaPi_Selector.py"])
        self.runningSS          =[]
        self.pid                = os.getpid()

        self.maapiDB.cleanSocketServerList()
        self.socketServer.runTcpServer(self.watcherHost, self.watcherPort)
        self.writePid(self.pid)

        signal.signal(signal.SIGTERM, self.service_shutdown)
        signal.signal(signal.SIGINT, self.service_shutdown)


    def service_shutdown(self, signum, frame):
        self.maapilogger.log("INFO",f'Caught signal {signum} | stoping MaaPi {self.objectname}')
        self.runningSS = self.maapiDB.table("maapi_running_socket_servers").get()

        payload = self.helpers.pyloadToPicke(777, " ", " ", " ", self.watcherHost,self.watcherPort)
        self.writePid("")

        for i in self.runningSS:
            self.socketClient.sendStr(self.runningSS[i]["ss_host"], self.runningSS[i]["ss_port"], payload)
        self.maapilogger.log("INFO",f'stoping {self.objectname}')
        raise SystemExit


    def writePid(self, pid):
        f = open(f"pid/MaaPi_{self.objectname}.socket.pid", "w")
        f.write(f"{pid}")
        f.close()


    def getRunnigSocketServers(self):
        self.runningSS = self.maapiDB.table("maapi_running_socket_servers").get()
        self.maapilogger.log("DEBUG","Update maapiCommandLine from database")


    def startSelectorModule(self):
        try:
            self.maapilogger.log("INFO", f"Killing Selector - {self.selectorPid.pid}")
            self.selectorPid.kill()
        except Exception as e:
            self.maapilogger.log("ERROR", e)
        else:
            self.selectorPid = subprocess.Popen([self.interpreterVer, "MaaPi_Selector.py"])
            self.maapilogger.log("INFO", f"Sterting Selector PID: {self.selectorPid.pid}")


    def checkSelector(self):
        try:
            if (dt.now() - self.lastResponce).seconds > 5:
                self.maapilogger.log("DEBUG", f"Sending query to Selector: is ok? {self.selectorHost}, {self.selectorPort}")
                payload = self.helpers.pyloadToPicke(00, " ", " ", " ", self.watcherHost,self.watcherPort)
                try:
                    recive =  self.socketClient.sendStrAndRecv(self.selectorHost, self.selectorPort, payload)
                except:
                    self.startSelectorModule()
                else:
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
    MaapiW =  MaapiWatcher()
    MaapiW.loop()