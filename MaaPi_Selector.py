
#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
##############################################################
#
#                          MAAPI 5.0
#                           Selector
#
##############################################################

import lib_maapi_socketServer               as SocketServer
import lib_maapi_socketClient               as SocketClient
import lib_maapi_queue                      as Queue
import lib_maapi_db_connection              as Db_connection
import MaaPi_Config                          as Config
import lib_maapi_helpers                    as Helpers

from threading import Lock, Thread
from datetime import datetime as dt, timedelta
import time
import copy
class MaapiSelector():

    def __init__(self):
        # objects
        self.queue              = Queue.Queue()
        self.config             = Config.MaapiVars()
        self.sendstr            = SocketClient.socketClient()
        self.socketServer       = SocketServer.SocketServer()
        self.maapiDB            = Db_connection.MaaPiDBConnection()
        self.helpers            = Helpers.Helpers()

        # vars
        self.board_id           = 0
        self.maapiLocation      = self.config.maapiLocation
        self.objectname         = "selector"
        self.selectorPort       = self.config.selectorPort
        self.selectorHost       = self.config.selectorHost
        self.thread             = []
        self.timer_1            = dt.now()
        self.timer_2            = dt.now()
        self.deviceList         = []
        self.libraryList        = []
        self.libraryList_id     = []
        self.devicesGroupedBylib= {}

        self.debug = 1
        self._debug(1,"Initialising Selector Module ")


    def __del__(self):
        self._debug(1,"Joining tcp server thread ")
        self.thread[0].join()


    def _debug(self, level, msg):
        if self.debug >= level:
            print("DEBUG | Selector \t| {0} {1},\t| {2}".format(level, dt.now(), msg))


    def runTcpServer(self):
        self._debug(2,"Selector run tcp Server")
        self.thread.append(Thread(target=self.socketServer.startServer,
            args=(self.objectname, self.selectorHost, self.selectorPort, self.queue, 1)))
        self.thread[0].start()


    def runLibraryDeamons(self):
        pass

    def to_sec(self, value, unit):
        _seconds = 0
        if unit == 2: _seconds = value * 60
        elif unit == 3: _seconds = value * 3600
        else: _seconds = value
        return _seconds

    def checkDbForOldreadings(self,devices):
        cache = {}
        for dev in devices:
            if (dt.now() - devices[dev]["dev_last_update"]).seconds > self.to_sec(devices[dev]["dev_interval"], devices[dev]["dev_interval_unit_id"]):
                self._debug(1,"Devices sended to checkout readings {Ex}".format(Ex=devices[dev]["dev_rom_id"]))
                self.queue.updateQueueDevList(devices[dev]["dev_type_id"],dev)
        #print (self.queue.getQueueDevList())



    def getLibraryList(self):
        self.libraryList = self.maapiDB.table("maapi_device_list").filters_eq(device_enabled = True, device_location_id = self.board_id).get()
        for ids in self.libraryList:
            self.queue.prepareQueueDevList(ids)
        self._debug(1,"Devices library list updated")


    def getDeviceList(self):
        board_location = self.maapiDB.table("maapi_machine_locations").filters_eq(ml_enabled = True).get()
        for i in board_location:
            if board_location[i]["ml_location"] == self.maapiLocation:
                self.board_id = board_location[i]["id"]

        self.deviceList = self.maapiDB.table("devices").columns(
                "dev_id",
                "dev_type_id",
                "dev_rom_id",
                "dev_bus_type_id",
                "dev_last_update",
                "dev_interval",
                "dev_interval_unit_id",
                "dev_interval_queue",
                "dev_machine_location_id",
                ).order_by('dev_id').filters_eq(
                dev_status = True, dev_machine_location_id = self.board_id).get()
        self._debug(1,"Devices list updated")

    def sendDataToServer(self,host,port,data):
        try:
            self.sendstr.sendStr(host, port, data)
        except Exception as e:
            self._debug(1,"Exception - SendDataToServer {Ex}".format(Ex=e))


    def loop(self):
        while True:
            if (dt.now() - self.timer_1).seconds > 5:
                self.getDeviceList()
                self.timer_1 = dt.now()
            if (dt.now() - self.timer_2).seconds > 60:
                self.getLibraryList()
            time.sleep(1)
            self.checkDbForOldreadings(self.deviceList)


    def startConf(self):
        self._debug(1,"Preparing to start ")
        self.getDeviceList()
        self.getLibraryList()


if __name__ == "__main__":
    MaapiSel =  MaapiSelector()
    MaapiSel.runTcpServer()
    MaapiSel.startConf()
    MaapiSel.loop()

