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
        self.board_id           = 99
        self.selectorHost       = self.config.selectorHost
        self.selectorPort       = self.config.selectorPort
        self.watcherHost        = self.config.watcherHost
        self.watcherPort        = self.config.watcherPort
        self.selecorName        = self.config.selectorName
        self.maapiLocation      = self.config.maapiLocation
        self.interpreterVer     = f"{sys.executable}"
        self.lastResponce       = dt.now() - timedelta(hours = 1)
        self.sendingQueryToSocket = 0

        self.socketServer       = SocketServer.SocketServer(self.objectname, self.queue, 1)
        self.runningSS          = []
        self.pid                = os.getpid()
        self.selectorPid        = object()

        self.socketServer.runTcpServer(self.watcherHost, self.watcherPort)
        self.writePid(self.pid)

        signal.signal(signal.SIGTERM, self.service_shutdown)
        signal.signal(signal.SIGINT, self.service_shutdown)

    def service_shutdown(self, signum, frame):
        self.maapilogger.log("INFO",f'Caught signal {signum} | stoping MaaPi {self.objectname}')
        self.runningSS = self.maapiDB.table("maapi_running_socket_servers").filters_eq(ss_board_id = self.board_id).get()
        self.maapiDB.cleanSocketServerList(self.board_id)

        payload = self.helpers.pyloadToPicke(777, " ", " ", " ", self.watcherHost,self.watcherPort)
        self.writePid("")
        for i in self.runningSS:
            self.maapilogger.log("INFO",f"stoping {self.runningSS[i]['ss_host']} {self.runningSS[i]['ss_port']} ")
            self.socketClient.sendStr(self.runningSS[i]["ss_host"], self.runningSS[i]["ss_port"], payload)

        payload_udp = "777_0_0_0"
        self.socketClient.sendViaUDP(self.config.selectorHost, 60000, bytes(payload_udp.encode()))
        self.maapilogger.log("INFO",f'stoping {self.objectname}')
        raise SystemExit


    def writePid(self, pid):
        f = open(f"pid/MaaPi_{self.objectname}.pid", "w")
        f.write(f"{pid}")
        f.close()

    def updateBoardLocation(self):
        board_location = self.maapiDB.table("maapi_machine_locations").filters_eq(ml_enabled = True).get()
        for i in board_location:
            if board_location[i]["ml_location"] == self.maapiLocation:
                self.board_id = board_location[i]["id"]



    def getRunnigSocketServers(self):
        self.runningSS = self.maapiDB.table("maapi_running_socket_servers").get()
        self.maapilogger.log("DEBUG","Update maapiCommandLine from database")


    def startSelectorModule(self):
        try:
            self.maapilogger.log("INFO", f"Killing Selector - {self.selectorPid.pid}")
            self.selectorPid.kill()
        except Exception as e:
            self.maapilogger.log("ERROR", f"startSelectorModule() {e}")
        finally:
            self.selectorPid = subprocess.Popen([self.interpreterVer, "MaaPi_Selector.py"])
            self.maapilogger.log("INFO", f"Sterting Selector PID: {self.selectorPid.pid}")
            self.maapiDB.insertRaw("maapi_running_py_scripts", ("default",
                                                                "'Selector'",
                                                                "'MaaPi_Selector.py'",
                                                                "now()",
                                                                f"{self.board_id}",
                                                                f"{self.selectorPid.pid }" ))


    def checkSelector(self):
        try:
            if (dt.now() - self.lastResponce).seconds > 5:
                if self.sendingQueryToSocket > 10:
                    self.maapilogger.log("INFO", f"Sending query to Selector: is ok? {self.selectorHost}, {self.selectorPort}")
                    self.sendingQueryToSocket = 0
                self.sendingQueryToSocket += 1
                payload = self.helpers.pyloadToPicke(00, " ", " ", " ", self.watcherHost,self.watcherPort)
                try:
                    recive =  self.socketClient.sendStrAndRecv(self.selectorHost, self.selectorPort, payload)
                except:
                    self.startSelectorModule()
                else:
                    if recive == bytes(0xff):
                        self.lastResponce = dt.now()

                        self.maapiDB.updateRaw("maapi_running_socket_servers ", " ss_last_responce = now() ", f" ss_host='{self.selectorHost}' and   ss_port='{self.selectorPort}'")
                    else:
                        self.startSelectorModule()
        except Exception as e :
            self.maapilogger.log("ERROR", "checkSelector() error: {exc}".format(exc = e))


    def loop(self):
        while True:
            time.sleep(self.loopInterval)
            self.checkSelector()


if __name__ == "__main__":
    MaapiW =  MaapiWatcher()
    MaapiW.updateBoardLocation()
    MaapiW.startSelectorModule()
    MaapiW.loop()