
#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
##############################################################
#
#                          MAAPI 5.0
#                           Selector
#
##############################################################
from threading import Lock, Thread
from datetime import datetime               as dt, timedelta
import lib_maapi_socketServer               as SocketServer
import lib_maapi_socketClient               as SocketClient
import lib_maapi_queue                      as Queue
import lib_maapi_db_connection              as Db_connection
import MaaPi_Config                          as Config
import lib_maapi_helpers                    as Helpers
import lib_checkDeviceCond                  as CheckDev
import lib_maapi_logger                     as MaapiLogger
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
        self.interpreterVer       ="/usr/bin/python{0}.{1}".format(sys.version_info[0],sys.version_info[1])
        # vars
        self.board_id           = 5
        self.maapiLocation      = self.config.maapiLocation
        self.selectorPort       = self.config.selectorPort
        self.selectorHost       = self.config.selectorHost
        self.thread             = []
        self.timer_1            = dt.now()
        self.timer_2            = dt.now()
        self.deviceList         = []
        self.libraryList        = []
        self.libraryList_id     = []
        self.selectorPid        = {}
        self.devicesGroupedBylib= {}
        self.localQueue         = {}

        self.socketServer       = SocketServer.SocketServer(self.objectname, self.selectorHost, self.selectorPort, self.queue, 1)
        self.socketServer.runTcpServer()

        self.maapilogger.log("INFO","Initialising Selector Module ")


    def __del__(self):
        self.maapilogger.log("INFO","Joining tcp server thread ")


    def runLibraryDeamons(self):

        for lib in self.libraryList:
            lists =[]
            lists.append(self.interpreterVer)
            lists.append(f"{self.libraryList[lib]['device_lib_name']}.py")
            lists.append(f"{self.selectorHost}")
            lists.append(f"{int(self.selectorPort)+int(self.libraryList[lib]['id'])}")
            lists.append(f"21")

            self.maapilogger.log("INFO","{}".format(self.libraryList[lib]["id"]))
            self.selectorPid[lib] = subprocess.Popen(lists)



    def checkDbForOldreadings(self):
        for dev in self.deviceList:
            lastUpdate = self.deviceList[dev]["dev_last_update"]
            interval   = self.deviceList[dev]["dev_interval"]
            interval_u = self.deviceList[dev]["dev_interval_unit_id"]
            tosec      = self.helpers.to_sec(interval, interval_u)
            if (dt.now() - lastUpdate).seconds >= tosec:
                try:
                    d = self.localQueue[dev]
                except:
                    self.maapilogger.log("ERROR",f"self.localQueue[dev] not exist {dev}")
                    self.localQueue[dev]=lastUpdate
                if (dt.now() - self.localQueue[dev]).seconds >= (tosec/2):
                    self.localQueue[dev]=dt.now()
                    payload = self.helpers.pyloadToPicke(10, self.deviceList[dev] , self.selectorHost,self.selectorPort)
                    self.maapilogger.log("INFO",f"Devices sended to checkout readings {self.deviceList[dev]['dev_id']} | {self.deviceList[dev]['dev_user_name']} | {self.deviceList[dev]['dev_rom_id']}")
                    try:
                        self.socketClient.sendStr(self.selectorHost, int(self.selectorPort)+int(self.deviceList[dev]["dev_type_id"]), payload)
                    except Exception as e:
                        self.maapilogger.log("ERROR","Exception - Send Data to lib {Ex}".format(Ex=e))
                        self.localQueue[dev]=lastUpdate


    def getLibraryList(self):
        self.libraryList = self.maapiDB.table("maapi_device_list").filters_eq(device_enabled = True, device_location_id = self.board_id).get()
        for ids in self.libraryList:
            self.queue.prepareQueueDevList(ids)
        self.maapilogger.log("DEBUG","Devices library list updated")


    def getDeviceList(self):
        board_location = self.maapiDB.table("maapi_machine_locations").filters_eq(ml_enabled = True).get()
        for i in board_location:
            if board_location[i]["ml_location"] == self.maapiLocation:
                self.board_id = board_location[i]["id"]
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
                dev_status = True, dev_machine_location_id = self.board_id).get()

        gdstop = dt.now()
        self.maapilogger.log("DEBUG","Devices list updated in time: {tim}".format(tim=(gdstop-gdstart)))

    def sendDataToServer(self,host,port,data):
        try:
            self.sendstr.sendStr(host, port, data)
        except Exception as e:
            self.maapilogger.log("ERROR","Exception - SendDataToServer {Ex}".format(Ex=e))

    def loop(self):
        while True:
            if (dt.now() - self.timer_1).seconds >= 1:
                self.timer_1 = dt.now()
                self.getDeviceList()

            if (dt.now() - self.timer_2).seconds >= 10:
                self.getLibraryList()
                self.timer_2 = dt.now()
            time.sleep(0.05)
            self.checkDbForOldreadings()


    def startConf(self):
        self.maapilogger.log("INFO","Preparing to start Selector module")
        self.getDeviceList()
        self.getLibraryList()


if __name__ == "__main__":
    MaapiSel =  MaapiSelector()
    MaapiSel.startConf()
    MaapiSel.runLibraryDeamons()
    MaapiSel.loop()
