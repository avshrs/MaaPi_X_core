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
        self.board_id           = self.helpers.updateBoardLocation(self.config.maapiLocation,self.maapiDB.table("maapi_machine_locations").filters_eq(ml_enabled = True).get())

        self.payload_StopTCP    = self.helpers.pyloadToPicke(777, " ", " ", " ", self.watcherHost,self.watcherPort)
        self.payload_Status     = self.helpers.pyloadToPicke(00, " ", " ", " ", self.watcherHost,self.watcherPort)
        self.payload_StopUDP    = "777_0_0_0"
        self.interpreterVer     = f"{sys.executable}"

        self.lastCheck          = dt.now()
        self.checkSended         = False
        self.responceS          = False
        self.SelectorResponce   = dt.now()
        self.sendingQueryToSocket = 0

        self.socketServer       = SocketServer.SocketServer(self.objectname, self.queue, self.board_id)
        self.runningSS          = []
        self.selectorPid        = object()
        self.socketServer.runTcpServer(self.watcherHost, self.watcherPort)
        signal.signal(signal.SIGTERM, self.service_shutdown)
        signal.signal(signal.SIGINT, self.service_shutdown)


    def service_shutdown(self, signum, frame):
        self.maapilogger.log("STOP",f'Caught signal {signum} | stoping MaaPi {self.objectname}')
        self.sendStopMessageToSocketServers()
        time.sleep(2)
        raise SystemExit


    def sendStopMessageToSocketServers(self):
        self.runningSocketService = self.maapiDB.table("maapi_running_socket_servers").get()
        for srv in self.runningSockSrv:
            if self.runningSockSrv[srv]['ss_board_id'] == self.board_id:
                if self.runningSockSrv[srv]['ss_type'] == "TCP":
                    self.socketClient.sendStr(self.runningSockSrv[srv]['ss_host'], self.runningSockSrv[srv]['ss_port'], self.payload_StopTCP)
                    self.maapilogger.log("STOP",f"Sending Stop message to TCP Service {self.runningSockSrv[srv]['ss_host']} {self.runningSockSrv[srv]['ss_port']}")
                if self.runningSockSrv[srv]['ss_type'] == "UDP":
                    self.socketClient.sendViaUDP(self.config.selectorHost, 60000, bytes(self.payload_StopUDP.encode()))
                    self.maapilogger.log("STOP",f"Sending Stop message to UDP Service {self.runningSockSrv[srv]['ss_host']} {self.runningSockSrv[srv]['ss_port']}")


    def startSelectorService(self):
        try:
            self.maapilogger.log("START", f"Starting Selector Service at host:{self.selectorHost}, port:{self.selectorPort}")
            self.selectorPid = subprocess.Popen([self.interpreterVer, "MaaPi_Selector.py"])
            self.maapilogger.log("START", f"Selector Service started at PID: {self.selectorPid.pid}")
            self.maapiDB.insertRaw("maapi_running_py_scripts", ("default", "'Selector'", "'MaaPi_Selector.py'", "now()", f"{self.board_id}", f"{self.selectorPid.pid }" ))
            self.maapilogger.log("START", f"Selector Service added to running service table in database.")
            self.lastCheck = dt.now()
        except Exception as e:
            self.maapilogger.log("ERROR", f"startSelectorService() | {e}")


    def stopSelectorService(self):
        try:
            self.maapilogger.log("STOP", f"Try to kill not responding Selector Service")
            try:
                self.maapilogger.log("STOP", f"Try to stop Selector Service - Socket Server")
                self.socketClient.sendStr(self.runningSS[i]['ss_host'], self.runningSS[i]['ss_port'], payload)
            except:
                self.maapilogger.log("STOP", f"Selector Service - Socket Server not running")
            self.selectorPid.kill()
        except:
            self.maapilogger.log("STOP", f"Selector Service - not started")
        else:
            self.maapilogger.log("STOP", f"Selector Service - Process Killed")


    def restartSelectorService(self):
        self.maapilogger.log("STATUS", f"Restrting Selector Service")
        self.stopSelectorService()
        self.startSelectorService()


    def checkSelectorStatus(self):
        if (dt.now() - self.lastCheck).seconds > 60 and not self.checkSended:
            self.maapilogger.log("STATUS", f"Checking Selector status")
            try:
                self.maapilogger.log("STATUS", f"Sending Query to {self.selectorHost}, {self.selectorPort} for status")
                self.socketClient.sendStr(self.selectorHost, self.selectorPort, self.payload_Status)
                self.checkSended = True
                self.responceS == False
                self.SelectorResponce= dt.now()
            except:
                self.maapilogger.log("STATUS", f"ERROR - Socket Server is not avalible {self.selectorHost}, {self.selectorPort} | Restarting")
                # self.restartSelectorService()


    def responceFromSelector(self):
        self.maapilogger.log("DEBUG", f"responceFromSelector()")
        if self.queue.getSocketStatusLen() > 0:
            self.maapilogger.log("STATUS", f"responceFromSelector() queue not empty")
            queueTmp  = self.queue.getSocketStatus()
            queue_ = queueTmp[self.objectname][self.selectorHost][self.selectorPort]
            for nr in queue_:
                self.maapilogger.log("STATUS", f"responceFromSelector() infor")
                if queue_[nr][0] == 0xff:
                    self.maapilogger.log("STATUS", f"Get Responce from Selector")
                    self.checkSended = False
                    self.responceS == True
                if queue_[nr][0] == 777:
                    self.service_shutdown()


    def checkSelectorResponceTime(self):
        if (dt.now() - self.SelectorResponce).seconds > 20 and self.checkSended and not self.responceS :
            self.maapilogger.log("STATUS", f"Selector Service - not responding | restarting")
            self.restartSelectorService()
            self.SelectorResponce = dt.now()


    def loop(self):
        while True:
            time.sleep(1)
            self.checkSelectorStatus()
            self.responceFromSelector()
            self.checkSelectorResponceTime()


if __name__ == "__main__":
    MaapiW =  MaapiWatcher()
    MaapiW.startSelectorService()
    MaapiW.loop()