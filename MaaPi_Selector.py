
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
import time
import copy


class MaapiSelector():

    def __init__(self):
        # objects
        self.queue              = Queue.Queue()
        self.config              = Config.MaapiVars()
        self.sendstr            = SocketClient.socketClient()
        self.objectname         = "Selector"

        self.maapiDB            = Db_connection.MaaPiDBConnection()
        self.helpers            = Helpers.Helpers()
        self.checkDev           = CheckDev.CheckDevCond()
        self.maapilogger        = MaapiLogger.Logger()
        self.maapilogger.name   = self.objectname
        self.interpreterVer       ="/usr/bin/python{0}.{1}".format(sys.version_info[0],sys.version_info[1])
        # vars
        self.board_id           = 0
        self.maapiLocation      = self.config.maapiLocation

        self.selectorPort       = self.config.selectorPort
        self.selectorHost       = self.config.selectorHost
        self.thread             = []
        self.timer_1            = dt.now()
        self.timer_2            = dt.now()
        self.deviceList         = []
        self.libraryList        = []
        self.libraryList_id     = []
        elf.selectorPid         = []
        self.devicesGroupedBylib= {}

        self.socketServer       = SocketServer.SocketServer(self.objectname, self.selectorHost, self.selectorPort, self.queue, 1)
        self.socketServer.runTcpServer()

        self.maapilogger.log("INFO","Initialising Selector Module ")


    def __del__(self):
        self.maapilogger.log("INFO","Joining tcp server thread ")



    def runLibraryDeamons(self):
        for lib in self.libraryList:
            self.maapilogger.log("INFO","{}".format(self.libraryList[lib][maapi_device_list]))
            self.selectorPid[lib] = subprocess.Popen([self.interpreterVer, "MaaPi_Selector.py {0} {1} {2}".format(
                self.selectorHost, int(self.selectorPort)+int(lib),lib )])


    def checkDbForOldreadings(self,devices):
        for dev in devices:
            lastUpdate = devices[dev]["dev_last_update"]
            interval   = devices[dev]["dev_interval"]
            interval_u = devices[dev]["dev_interval_unit_id"]
            if (dt.now() - lastUpdate).seconds > self.helpers.to_sec(interval, interval_u):
                self.maapilogger.log("DEBUG","Devices sended to checkout readings {Ex}".format(Ex=devices[dev]["dev_rom_id"]))
                self.queue.updateQueueDevList(devices[dev]["dev_type_id"],dev)
                payload = self.helpers.pyloadToPicke(00, dev , self.selectorHost,self.selectorPort)
                recive =  self.socketClient.sendStrAndRecv(self.selectorHost, int(self.selectorPort)+int(libdevices[dev]["dev_type_id"]), payload)


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
            if (dt.now() - self.timer_1).seconds >=1:
                self.getDeviceList()
                self.timer_1 = dt.now()
            if (dt.now() - self.timer_2).seconds >= 60:
                self.getLibraryList()
                self.timer_2
            time.sleep(0.1)
            self.checkDbForOldreadings(self.deviceList)


    def startConf(self):
        self.maapilogger.log("INFO","Preparing to start Selector module")
        self.getDeviceList()
        self.getLibraryList()


if __name__ == "__main__":
    MaapiSel =  MaapiSelector()
    MaapiSel.startConf()
    MaapiSel.loop()

