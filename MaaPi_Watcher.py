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
        print ("startnig wacher")
        self.selectorHost       = self.config.selectorHost
        self.selectorPort       = self.config.selectorPort
        self.watcherHost        = self.config.watcherHost
        self.watcherPort        = self.config.watcherPort
        self.selecorName        = self.config.selectorName
        self.board_id           = self.helpers.updateBoardLocation(self.config.maapiLocation,self.maapiDB.table("maapi_machine_locations").filters_eq(ml_enabled = True).get())
        self.interpreterVer     = f"{sys.executable}"
        self.lastResponce       = dt.now() - timedelta(hours = 1)
        self.sendingQueryToSocket = 0

        self.socketServer       = SocketServer.SocketServer(self.objectname, self.queue, self.board_id)
        self.runningSS          = []
        self.selectorPid        = object()

        self.socketServer.runTcpServer(self.watcherHost, self.watcherPort)

        signal.signal(signal.SIGTERM, self.service_shutdown)
        signal.signal(signal.SIGINT, self.service_shutdown)


    def service_shutdown(self, signum, frame):
        self.maapilogger.log("STOP",f'Caught signal {signum} | stoping MaaPi {self.objectname}')
        self.runningSS = self.maapiDB.table("maapi_running_socket_servers").filters_eq(ss_board_id = self.board_id).get()
        self.maapiDB.cleanSocketServerList(self.board_id)

        payload = self.helpers.pyloadToPicke(777, " ", " ", " ", self.watcherHost,self.watcherPort)


        for i in self.runningSS:
            if self.runningSS[i]['ss_port'] !=  self.config.udpListenerPort:
                self.maapilogger.log("STOP",f"stoping {self.runningSS[i]['ss_host']} {self.runningSS[i]['ss_port']}")
                self.socketClient.sendStr(self.runningSS[i]["ss_host"], self.runningSS[i]["ss_port"], payload)
            else:
                payload_udp = "777_0_0_0"
                self.socketClient.sendViaUDP(self.config.selectorHost, 60000, bytes(payload_udp.encode()))
                self.maapilogger.log("STOP",f'stoping {self.objectname}')

        raise SystemExit


    def startSelectorModule(self):
        try:
            self.maapilogger.log("STOP", f"Killing Selector - {self.selectorPid.pid}")
            self.selectorPid.kill()
        except Exception as e:
            self.maapilogger.log("ERROR", f"Can't stop Selector not running - {e}")
        finally:
            self.selectorPid = subprocess.Popen([self.interpreterVer, "MaaPi_Selector.py"])
            self.maapilogger.log("START", f"Sterting Selector PID: {self.selectorPid.pid}")
            self.maapiDB.insertRaw("maapi_running_py_scripts", ("default",
                                                                "'Selector'",
                                                                "'MaaPi_Selector.py'",
                                                                "now()",
                                                                f"{self.board_id}",
                                                                f"{self.selectorPid.pid }" ))


    def checkSelector(self):
        try:
            if (dt.now() - self.lastResponce).seconds > 5:
                if self.sendingQueryToSocket > 12:
                    self.maapilogger.log("DEBUG", f"Sending query to Selector: is ok? {self.selectorHost}, {self.selectorPort}")
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

                        self.maapiDB.updateRaw("maapi_running_socket_servers ", " ss_last_responce = now() ", f" ss_host='{self.selectorHost}' and   ss_port='{self.selectorPort}' and ss_board_id={self.board_id}")
                    else:
                        self.startSelectorModule()
        except Exception as e :
            self.maapilogger.log("ERROR", "checkSelector() error: {exc}".format(exc = e))


    def loop(self):
        while True:
            time.sleep(0.1)
            self.checkSelector()


if __name__ == "__main__":
    MaapiW =  MaapiWatcher()
    MaapiW.startSelectorModule()
    MaapiW.loop()