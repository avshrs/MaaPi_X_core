#!/usr/bin/python3.7
# -*- coding: utf-8 -*-import sys
###############################################################
#
#                          MAAPI X
#
##############################################################


import time
import os
import sys
import signal
import psutil
import lib_maapi_main_socketServer as SocketServer
from datetime import datetime as dt
from lib_maapi_service_class import serviceClass
from threading import Thread


class MaapiWatcher(serviceClass):
    """Main class of MaaPi application"""

    def __init__(self):
        super().__init__()
        self.objectname = "Watcher"
        self.timer_1 = dt.now()
        self.timer_2 = dt.now()
        self.timer_3 = dt.now()
        self.timer_4 = dt.now()
        self.interpreterVer = f"{sys.executable}"
        self.libraryList = []
        self.selectorPid = object()
        self.pid = os.getpid()
        self.maapiDB.cleanSocketServerList(self.board_id)
        self.maapiDB.insertRaw(
            "maapi_running_py_scripts", (
                "default",
                f"'{self.objectname}'",
                f"'MaaPi_{self.objectname}.py'",
                "now()",
                f"{self.board_id}",
                f"{self.pid}"
                )
            )
        self.socketServer = SocketServer.SocketServer(
            self.objectname,
            self.queue,
            self.board_id
            )
        self.maapilogger.name = self.objectname
        self.watcherHost = self.config.watcherHost
        self.watcherPort = self.config.watcherPort
        self.socketServer.runTcpServer(self.watcherHost, self.watcherPort)

        signal.signal(signal.SIGTERM, self.service_shutdown)
        signal.signal(signal.SIGINT, self.service_shutdown)

    def service_shutdown(self, signum, frame):
        self.running = False
        self.maapilogger.log(
            "STOP",
            f'Caught signal {signum} | stoping MaaPi {self.objectname}'
            )
        self.stopServiceViaTCP(self.selectorHost, self.selectorPort)
        self.maapiDB.cleanSocketServerList(self.board_id)

        for process in self.libraryPID:
            self.stopServiceViaTCP(
                self.libraryPID[process]["host"],
                self.libraryPID[process]["port"]
                )
        self.stopServiceViaTCP(self.watcherHost, self.watcherPort)
        raise SystemExit

    def setUp(self):
        self.maapilogger.log("INFO", "Running Set UP ")
        self.getLibraryList()
        self.startAllLibraryDeamon()

        self.startSelectorServices(
            self.selectorHost,
            self.selectorPort,
            "MaaPi_Selector"
            )

    def checkPIDsParameters(self):
        """check pids cpu and mem usage"""
        # selector
        self.maapiDB.updateRaw(
            "maapi_running_py_scripts",
            f"py_mem_usage={round(psutil.Process(self.selectorPid.pid).memory_info()[0]/1000000,3)}",
            f"py_pid={self.selectorPid.pid}"
            )
        self.maapiDB.updateRaw(
            "maapi_running_py_scripts",
            f"py_cpu_usage={round(psutil.Process(self.selectorPid.pid).cpu_percent(interval=1),3)}",
            f"py_pid={self.selectorPid.pid}")

        # watcher
        self.maapiDB.updateRaw(
            "maapi_running_py_scripts",
            f"py_mem_usage={round(psutil.Process(self.pid).memory_info()[0]/1000000,3)}",
            f"py_pid={self.pid}"
            )

        self.maapiDB.updateRaw(
            "maapi_running_py_scripts",
            f"py_cpu_usage={round(psutil.Process(self.pid).cpu_percent(interval=1),3)}",
            f"py_pid={self.pid}"
            )

        # chek rest of library
        for process in self.libraryPID:
            pider = self.libraryPID[process]["pid"].pid
            try:
                pider = self.libraryPID[process]["pid"].pid

                self.maapiDB.updateRaw(
                    "maapi_running_py_scripts",
                    f"py_mem_usage={round(psutil.Process(pider).memory_info()[0]/1000000,3)}",
                    f"py_pid={pider}"
                    )

                self.maapiDB.updateRaw(
                    "maapi_running_py_scripts",
                    f"py_cpu_usage={round(psutil.Process(pider).cpu_percent(interval=1),3)}",
                    f"py_pid={pider}"
                    )

            except Exception as error:
                self.maapilogger.log(
                    "ERROR",
                    f"error at updateing pid "
                    f"{pider} stats error:{error}"
                    )

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

                thread = Thread(target=self.checkPIDsParameters())
                thread.start()

            if (dt.now() - self.timer_4).seconds >= 10000:
                self.timer_4 = dt.now()
                self.maapiDB.clean_logs()

            self.checkLibraryResponce()
            time.sleep(0.01)


if __name__ == "__main__":
    MaapiW = MaapiWatcher()
    MaapiW.setUp()
    MaapiW.loop()