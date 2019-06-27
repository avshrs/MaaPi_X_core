#!/usr/bin/python3.7
# -*- coding: utf-8 -*-import sys
###############################################################
#
#                          MAAPI X
#
##############################################################
import lib_maapi_main_socketServer as SocketServer
import lib_maapi_main_socketClient as SocketClient
import lib_maapi_main_queue as Queue
import lib_maapi_main_dbconn as Db_connection
import lib_maapi_main_helpers as Helpers
import lib_maapi_main_checkDevCond as CheckDev
import lib_maapi_main_logger as MaapiLogger
import MaaPi_Config as Config
from datetime import datetime as dt, timedelta
import time
import copy
import sys
import os
import signal
import subprocess

class MaapiSelector():
    def __init__(self):
        # objects
        self.queue = Queue.Queue()
        self.config = Config.MaapiVars()
        self.socketClient = SocketClient.socketClient()
        self.objectname = "Selector"
        self.maapiDB = Db_connection.MaaPiDBConnection()
        self.helpers = Helpers.Helpers()
        self.checkDev = CheckDev.CheckDevCond()
        self.maapilogger = MaapiLogger.Logger()
        self.maapilogger.name = self.objectname
        self.interpreterVer = f"{sys.executable}"
        self.selectorPort = self.config.selectorPort
        self.selectorHost = self.config.selectorHost
        self.board_id = self.helpers.updateBoardLocation(self.config.maapiLocation,self.maapiDB.table("maapi_machine_locations").filters_eq(ml_enabled = True).get())
        self.payload_Status = self.helpers.pyloadToPicke(0xff, " ", " ", " ", self.selectorHost,self.selectorPort)
        self.maapiLocation = self.config.maapiLocation
        self.timeToRead = 0.05 # 0.05 = 5%  interval - time to read
        self.timer_1 = dt.now()
        self.timer_2 = dt.now()
        self.timer_3 = dt.now()
        self.deviceList = []
        self.libraryList = []
        self.libraryList_id = []
        self.runningServices = []
        self.devicesGroupedBylib = {}
        self.localQueue = {}
        self.libraryLastResponce = 10 # seconds
        self.socketServer = SocketServer.SocketServer(self.objectname, self.queue, 1)
        self.socketServer.runTcpServer(self.selectorHost, self.selectorPort)
        self.maapilogger.log("INFO", "Initialising Selector Module ")
        self.skippDev = []
        self.skippDevlib = {}
        self.pid = os.getpid()
        self.sendingQueryToSocket = 0
        signal.signal(signal.SIGTERM, self.service_shutdown)
        signal.signal(signal.SIGINT, self.service_shutdown)
        self.isRunning = True

    def service_shutdown(self, signum=None, frame=None):
        self.maapilogger.log("INFO", f'Caught signal {signum} | stoping MaaPi {self.objectname}')
        raise SystemExit

    def responceToWatcher(self):
        if self.queue.getSocketStatusLen() > 0:
            queue_ = (self.queue.getSocketStatus())[self.objectname][self.selectorHost][self.selectorPort]
            for nr in queue_:
                if queue_[nr][0] == 0:
                    self.maapilogger.log("STATUS", f"Get Query from Watcher")
                    try:
                        self.maapilogger.log("STATUS", f"Sending responce to Wacher {queue_[nr][4]} {queue_[nr][5]}")
                        self.socketClient.sendStr(queue_[nr][4], queue_[nr][5], self.payload_Status)
                    except Exception as e:
                        self.maapilogger.log("ERROR", f"Watcher Socket Server Not exist")
                elif queue_[nr][0] == 777:
                    self.service_shutdown()

    def sendToRunningService(self, dev):
        """Send message to running service"""
        payload = self.helpers.pyloadToPicke(
            10,
            dev,
            self.deviceList,
            self.deviceListForRelated,
            self.selectorHost,
            self.selectorPort
            )
        for serv in self.runningServices:
            if self.runningServices[serv]["ss_device_table_id"] == self.deviceList[dev]['dev_type_id']:
                try:
                    self.socketClient.sendStr(
                        self.runningServices[serv]["ss_host"],
                        self.runningServices[serv]["ss_port"],
                        payload)
                    self.maapilogger.log(
                        "DEBUG",
                        f"Devices sended to checkout readings {dev} | "
                        f"{self.deviceList[dev]['dev_user_name']} | "
                        f"{self.deviceList[dev]['dev_rom_id']} to "
                        f"{self.runningServices[serv]['ss_port']}"
                        )
                except Exception as error:
                    self.maapilogger.log(
                        "ERROR",
                        f"Exception checkDbForOldreadings - Send dev_id: "
                        f"{dev} to lib: {self.deviceList[dev]['dev_type_id']} "
                        f"library for dev not exist in database for this location/board{error}"
                        )

    def checkDbForOldreadings(self):
        for dev in self.deviceList:
            try:
                tosec = self.helpers.to_sec(
                    self.deviceList[dev]["dev_interval"],
                    self.deviceList[dev]["dev_interval_unit_id"]
                    )
                sensLastRead = (dt.now() - self.deviceList[dev]["dev_last_update"]).total_seconds()
                sensInterval = (tosec - (tosec * self.timeToRead))

                try:
                    localQueueCond = (dt.now() - self.localQueue[dev]).total_seconds()
                    print("tosec", tosec)
                    print("sensLastRead", sensLastRead)
                    print("sensInterval", sensInterval)
                    print("localQueueCond", localQueueCond)
                    time.sleep(0.01)
                    if sensLastRead >= sensInterval and localQueueCond >= tosec:
                        self.localQueue[dev] = dt.now()
                        self.sendToRunningService(dev)

                except Exception as e:
                    self.maapilogger.log(
                        "DEBUG",
                        f"Exception checkDbForOldreadings inner error: {e}"
                        )
                    if sensLastRead >= sensInterval:
                        self.localQueue[dev] = dt.now()
                        self.sendToRunningService(dev)
            except Exception as e:
                self.maapilogger.log(
                    "DEBUG",
                    f"Exception checkDbForOldreadings outer error: {e}"
                    )

    def getData(self):
        self.deviceList = self.maapiDB.table("devices").columns(
            "dev_id",
            "dev_type_id",
            "dev_rom_id",
            "dev_user_name",
            "dev_bus_type_id",
            "dev_bus_options_id",
            "dev_last_update",
            "dev_interval",
            "dev_value",
            "dev_unit_id",
            "dev_gpio_pin",
            "dev_interval_unit_id",
            "dev_interval_queue",
            "dev_machine_location_id",
            "dev_collect_values_to_db",
            "dev_collect_values_if_cond_e",
            "dev_collect_values_if_cond_min_e",
            "dev_collect_values_if_cond_max_e",
            "dev_collect_values_if_cond_max",
            "dev_collect_values_if_cond_min",
            "dev_collect_values_if_cond_from_dev_e",
            "dev_collect_values_if_cond_from_dev_id",
            "dev_collect_values_if_cond_force_value_e",
            "dev_collect_values_if_cond_force_value",
            ).order_by('dev_id').filters_eq(
            dev_status=True, dev_machine_location_id=self.board_id).get()

        self.deviceListForRelated = self.maapiDB.table("devices").columns(
            "dev_id",
            "dev_last_update",
            "dev_interval",
            "dev_value",
            "dev_interval_unit_id",
            ).order_by('dev_id').filters_eq(dev_status=True).get()

        self.runningServices = self.maapiDB.table(
            "maapi_running_socket_servers"
            ).filters_eq(ss_board_id=self.board_id).get()

    def loop(self):
        while self.isRunning:
            if (dt.now() - self.timer_2).seconds >= 5:
                self.getData()
                self.timer_2 = dt.now()
            time.sleep(0.01)
            self.checkDbForOldreadings()
            self.responceToWatcher()

    def startConf(self):
        self.maapilogger.log("INFO", "Preparing to start Selector module")
        self.getData()

if __name__ == "__main__":
    MaapiSel =  MaapiSelector()
    MaapiSel.startConf()
    MaapiSel.loop()
