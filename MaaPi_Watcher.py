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
from  lib_maapi_service_class import serviceClass
import lib_maapi_main_queue         as Queue

import lib_maapi_main_socketServer  as SocketServer
import MaaPi_Config                 as Config


class MaapiWatcher(serviceClass):
    def __init__(self):
        self.objectname         = "Watcher"
        self.selfkillsig        = False
        super().__init__()

        self.queue              = Queue.Queue()
        self.socketServer       = SocketServer.SocketServer(self.objectname, self.queue, self.board_id)

        self.selectorHost       = self.config.selectorHost
        self.selectorPort       = self.config.selectorPort
        self.watcherHost        = self.config.watcherHost
        self.watcherPort        = self.config.watcherPort
        self.selecorName        = self.config.selectorName

        self.payload_StopTCP    = self.helpers.pyloadToPicke(777, " ", " ", " ", self.watcherHost,self.watcherPort)
        self.payload_Status     = self.helpers.pyloadToPicke(00, " ", " ", " ", self.watcherHost,self.watcherPort)
        self.payload_StopUDP    = "777_0_0_0"

        self.timer_1            = dt.now()
        self.timer_2            = dt.now()
        self.interpreterVer     = f"{sys.executable}"
        self.libraryList        = []
        self.lastCheck          = dt.now()
        self.checkSended        = False
        self.responceS          = False
        self.SelectorResponce   = dt.now()
        self.sendingQueryToSocket = 0
        self.running            = True
        self.runningSS          = []
        self.maapiDB.cleanSocketServerList(self.board_id)
        self.selectorPid        = object()
        self.socketServer.runTcpServer(self.watcherHost, self.watcherPort)
        signal.signal(signal.SIGTERM, self.service_shutdown)
        signal.signal(signal.SIGINT, self.service_shutdown)

    def service_shutdown(self, signum, frame):
        self.running = False
        self.maapilogger.log("STOP",f'Caught signal {signum} | stoping MaaPi {self.objectname}')
        self.stopServiceViaTCP(self.selectorHost, self.selectorPort)
        self.maapiDB.cleanSocketServerList(self.board_id)
        for process in self.libraryPID:
            self.stopServiceViaTCP(self.libraryPID[process]["host"],self.libraryPID[process]["port"])
        self.stopServiceViaTCP(self.watcherHost, self.watcherPort)

        time.sleep(1)
        raise SystemExit


    def setUp(self):
        self.maapilogger.log("INFO","Running Set UP ")
        self.getLibraryList()
        self.startAllLibraryDeamon()
        self.startSelectorServices(self.selectorHost, self.selectorPort, "MaaPi_Selector")

    def loop(self):
        while self.running:
            if (dt.now() - self.timer_1).seconds >= 1:
                if self.running:
                    self.checkLibraryProcess()
                    self.checkLibraryResponce()
                self.timer_1 = dt.now()

            if (dt.now() - self.timer_2).seconds >= 5:
                self.timer_2 = dt.now()
                self.getLibraryList()
            time.sleep(0.01)




if __name__ == "__main__":
    MaapiW =  MaapiWatcher()
    MaapiW.setUp()
    MaapiW.loop()