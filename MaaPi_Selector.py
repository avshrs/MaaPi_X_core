#!/usr/bin/python3.7
# -*- coding: utf-8 -*-import sys
###############################################################
#
#                          MAAPI X
#
##############################################################
import lib_maapi_main_socketServer               as SocketServer
import lib_maapi_main_socketClient               as SocketClient
import lib_maapi_main_queue                      as Queue
import lib_maapi_main_dbORM                      as Db_connection
import lib_maapi_main_helpers                    as Helpers
import lib_maapi_main_checkDevCond               as CheckDev
import lib_maapi_main_logger                     as MaapiLogger
import MaaPi_Config                               as Config
from datetime import datetime                    as dt, timedelta
import time, copy, sys
import subprocess


class MaapiSelector():

    def __init__(self):
        # objects
        self.queue              = Queue.Queue()
        self.config              = Config.MaapiVars()
        self.socketClient       = SocketClient.socketClient()
        self.objectname         = "Selector"
        self.maapiDB            = Db_connection.MaaPiDBConnection()
        self.helpers            = Helpers.Helpers()
        self.checkDev           = CheckDev.CheckDevCond()
        self.maapilogger        = MaapiLogger.Logger()
        self.maapilogger.name   = self.objectname
        self.interpreterVer       =f"{sys.executable}"
        # vars
        self.board_id           = 99
        self.maapiLocation      = self.config.maapiLocation
        self.selectorPort       = self.config.selectorPort
        self.selectorHost       = self.config.selectorHost
        self.thread             = []
        self.timer_1            = dt.now()
        self.timer_2            = dt.now()
        self.timer_3            = dt.now()
        self.deviceList         = []
        self.libraryList        = []
        self.libraryList_id     = []
        self.libraryPID         = {}
        self.devicesGroupedBylib= {}
        self.localQueue         = {}
        self.libraryLastResponce= 10 # seconds
        self.socketServer       = SocketServer.SocketServer(self.objectname, self.queue, 1)
        self.socketServer.runTcpServer(self.selectorHost, self.selectorPort)
        self.maapilogger.log("INFO","Initialising Selector Module ")
        self.skippDev           = []


    def __del__(self):
        self.maapilogger.log("INFO","Joining tcp server thread ")

    def startlibraryDeamon(self):
        for lib in self.libraryList:
            try:
                self.runLibraryDeamon(lib, False)
                self.maapilogger.log("INFO", f"Starting library deamon {self.libraryList[lib]['device_lib_name']}")

            except Exception as e :
                self.maapilogger.log("Exception", "Error: startlibraryDeamon() {exc}".format(exc = e))

    def restartlibraryDeamon(self, lib_id):
        try:
            self.maapilogger.log("INFO", f"Killing not respondign library deamon {self.libraryList[lib]['device_lib_name']}")
            if self.libraryPID[lib_id]:
                self.libraryPID[lib_id]["pid"].kill()
                del self.libraryPID[lib_id]
        finally:
            self.runLibraryDeamon(lib_id, False)
            self.maapilogger.log("INFO", f"Restarting library deamon {self.libraryList[lib]['device_lib_name']}")


    def runLibraryDeamon(self, lib, force):
        try:
            if lib not in self.libraryPID[lib] or force:
                lists =[]
                lists.append(self.interpreterVer)                                               # interpreter version
                lists.append(f"{self.libraryList[lib]['device_lib_name']}.py")                  # library file name
                lists.append(f"{self.selectorHost}")                                            # host
                lists.append(f"{int(self.selectorPort)+int(self.libraryList[lib]['id'])}")      # port selector port + library unique index
                lists.append(f"{self.libraryList[lib]['id']}")                                  # library index

                pid = subprocess.Popen(lists)
                name = self.libraryList[lib]['device_lib_name']
                host = self.selectorHost
                port = int(self.selectorPort)+int(self.libraryList[lib]['id'])
                self.libraryPID[lib] = {
                            "id"   : lib,
                            "name" : name,
                            "pid"  : pid,
                            "host" : host,
                            "port" : port,
                            "lastResponce":dt.now()
                }
        except Exception as e :
            self.maapilogger.log("ERROR", "Exception: runLibraryDeamon() {exc}".format(exc = e))

    def checkLibraryProcess(self):
        for lib in self.libraryPID:
            try:
                if (dt.now() - self.libraryPID[lib]["lastResponce"]).seconds > self.libraryLastResponce:
                    self.maapilogger.log("INFO", f"Sending query to Selector: is ok? {self.libraryPID[lib]['name']} {self.libraryPID[lib]['host']}, {self.libraryPID[lib]['port']}")

                    payload = self.helpers.pyloadToPicke(00, " ", " ", " ",self.selectorHost,self.selectorPort)
                    try:
                        recive =  self.socketClient.sendStrAndRecv(self.libraryPID[lib]["host"], self.libraryPID[lib]["port"], payload)
                    except:
                        self.restartlibraryDeamon(lib)
                    else:
                        if recive == bytes(0xff):
                            self.libraryPID[lib]["lastResponce"] = dt.now()
                            self.maapilogger.log("INFO", "Get responce from selector")
                        else:
                            self.restartlibraryDeamon(lib)
            except Exception as e :
                self.maapilogger.log("ERROR", "Exception: runLibraryDeamon() {exc}".format(exc = e))


    def checkDbForOldreadings(self):
        for dev in self.deviceList:
            c_dev = self.deviceList[dev]
            tosec = self.helpers.to_sec(c_dev["dev_interval"], c_dev["dev_interval_unit_id"])

            if (dt.now() - c_dev["dev_last_update"]).seconds >= tosec and dev not in self.skippDev:
                try:
                    self.localQueue[dev]

                except:
                    self.localQueue[dev]=c_dev["dev_last_update"]
                    self.maapilogger.log("DEBUG",f"self.localQueue[dev] not exist - adding new{dev}")

                if (dt.now() - self.localQueue[dev]).seconds >= (tosec/2):
                    self.localQueue[dev]=dt.now()
                    payload = self.helpers.pyloadToPicke(10, dev, self.deviceList, self.deviceListForRelated, self.selectorHost,self.selectorPort)
                    self.maapilogger.log("DEBUG",f"Devices sended to checkout readings {dev} | {self.deviceList[dev]['dev_user_name'].encode('utf-8').strip()} | {self.deviceList[dev]['dev_rom_id']}")

                    try:
                        pid = self.libraryPID[self.deviceList[dev]['dev_type_id']]
                        self.socketClient.sendStr(pid["host"], pid["port"], payload)

                    except Exception as e:
                        self.maapilogger.log("ERROR",f"Exception checkDbForOldreadings - Send dev_id: {dev} to lib: {self.deviceList[dev]['dev_type_id']} library for dev not exist  - error: {e}")
                        self.skippDev.append(dev)
                        self.localQueue[dev]=c_dev["dev_last_update"]


    def getLibraryList(self):
        self.libraryList = self.maapiDB.table("maapi_device_list").filters_eq(device_enabled = True, device_location_id = self.board_id).get()

        for ids in self.libraryList:
            self.queue.prepareQueueDevList(ids)

        self.maapilogger.log("DEBUG","Devices library list updated")


    def updateBoardLocation(self):
        board_location = self.maapiDB.table("maapi_machine_locations").filters_eq(ml_enabled = True).get()

        for i in board_location:
            if board_location[i]["ml_location"] == self.maapiLocation:
                self.board_id = board_location[i]["id"]


    def getDeviceList(self):
        gdstart = dt.now()

        self.deviceList = self.maapiDB.table("devices").columns(
                "dev_id",
                "dev_type_id",
                "dev_rom_id",
                "dev_user_name",
                "dev_bus_type_id",
                "dev_last_update",
                "dev_interval",
                "dev_value",
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
                dev_status = True, dev_machine_location_id=self.board_id).get()

        self.deviceListForRelated = self.maapiDB.table("devices").columns(
                "dev_id",
                "dev_last_update",
                "dev_interval",
                "dev_value",
                "dev_interval_unit_id",
                ).order_by('dev_id').filters_eq(
                dev_status = True).get()

        gdstop = dt.now()
        self.maapilogger.log("DEBUG","Devices list updated in time: {tim}".format(tim=(gdstop-gdstart)))

    def sendDataToServer(self,host,port,data):
        try:
            self.sendstr.sendStr(host, port, data)
        except Exception as e:
            self.maapilogger.log("ERROR","Exception - SendDataToServer {Ex}".format(Ex=e))

    def loop(self):
        while True:
            if (dt.now() - self.timer_1).seconds >= 5:
                self.timer_1 = dt.now()
                self.getDeviceList()

            if (dt.now() - self.timer_2).seconds >= 10:
                self.getLibraryList()
                self.checkLibraryProcess()
                self.timer_2 = dt.now()

            if (dt.now() - self.timer_3).seconds >= 60:
                self.skippDev = []
                self.timer_3 = dt.now()

            time.sleep(0.1)
            self.checkDbForOldreadings()


    def startConf(self):
        self.maapilogger.log("INFO","Preparing to start Selector module")
        self.updateBoardLocation()
        self.getDeviceList()
        self.getLibraryList()


if __name__ == "__main__":
    MaapiSel =  MaapiSelector()
    MaapiSel.startConf()
    MaapiSel.startlibraryDeamon()
    time.sleep(1)
    MaapiSel.loop()
