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
from  lib_maapi_service_class import serviceClass
import lib_maapi_main_queue         as Queue
import psutil
import lib_maapi_main_socketServer  as SocketServer
import MaaPi_Config                 as Config
from threading import Lock, Thread

class MaapiWatcher(serviceClass):
    def __init__(self):
        self.objectname         = "Watcher"
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
        self.timer_3            = dt.now()
        self.timer_4            = dt.now()
        self.interpreterVer     = f"{sys.executable}"
        self.libraryList        = []
        self.running            = True
        self.selectorPid        = object()
        self.pid                = os.getpid()
        self.maapiDB.cleanSocketServerList(self.board_id)
        self.socketServer.runTcpServer(self.watcherHost, self.watcherPort)
        self.maapiDB.insertRaw("maapi_running_py_scripts", ("default", f"'{self.objectname}'", f"'MaaPi_{self.objectname}.py'", "now()", f"{self.board_id}", f"{self.pid}" ))
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


        raise SystemExit

    def setUp(self):
        self.maapilogger.log("INFO","Running Set UP ")
        self.getLibraryList()
        self.startAllLibraryDeamon()
        self.startSelectorServices(self.selectorHost, self.selectorPort, "MaaPi_Selector")

    def checkPIDs(self):
        # selector
        self.maapiDB.updateRaw("maapi_running_py_scripts",f"py_mem_usage={round(psutil.Process(self.selectorPid.pid).memory_info()[0]/1000000,3)}", f"py_pid={self.selectorPid.pid}")
        self.maapiDB.updateRaw("maapi_running_py_scripts",f"py_cpu_usage={round(psutil.Process(self.selectorPid.pid).cpu_percent(interval=1),3)}", f"py_pid={self.selectorPid.pid}")
        # watcher
        self.maapiDB.updateRaw("maapi_running_py_scripts",f"py_mem_usage={round(psutil.Process(self.pid).memory_info()[0]/1000000,3)}", f"py_pid={self.pid}")
        self.maapiDB.updateRaw("maapi_running_py_scripts",f"py_cpu_usage={round(psutil.Process(self.pid).cpu_percent(interval=1),3)}", f"py_pid={self.pid}")
        for process in self.libraryPID:
            pider = self.libraryPID[process]["pid"].pid
            try:
                pider = self.libraryPID[process]["pid"].pid
                self.maapiDB.updateRaw("maapi_running_py_scripts",f"py_mem_usage={round(psutil.Process(pider).memory_info()[0]/1000000,3)}", f"py_pid={pider}")
                self.maapiDB.updateRaw("maapi_running_py_scripts",f"py_cpu_usage={round(psutil.Process(pider).cpu_percent(interval=1),3)}", f"py_pid={pider}")
            except Exception as e:
                self.maapilogger.log("ERROR",f'error at updateing pid {pider} stats ')


    def loop(self):
        while self.running:
            if (dt.now() - self.timer_1).seconds >= 1:
                if self.running:
                    self.checkLibraryProcess()

                self.timer_1 = dt.now()

            if (dt.now() - self.timer_2).seconds >= 5:
                self.timer_2 = dt.now()
                self.getLibraryList()

            if (dt.now() - self.timer_3).seconds >= 60:
                self.timer_3 = dt.now()

                thread = Thread(target= self.checkPIDs())
                thread.start()

            if (dt.now() - self.timer_4).seconds >= 10000:
                self.timer_4 = dt.now()
                self.maapiDB.clean_logs()



            self.checkLibraryResponce()
            time.sleep(0.01)

if __name__ == "__main__":
    MaapiW =  MaapiWatcher()
    MaapiW.setUp()
    MaapiW.loop()