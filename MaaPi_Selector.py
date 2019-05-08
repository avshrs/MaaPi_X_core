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
import time, copy, sys, os, signal
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
        self.selectorPort       = self.config.selectorPort
        self.selectorHost       = self.config.selectorHost
        self.board_id           = self.helpers.updateBoardLocation(self.config.maapiLocation,self.maapiDB.table("maapi_machine_locations").filters_eq(ml_enabled = True).get())
        self.payload_Status     = self.helpers.pyloadToPicke(0xff, " ", " ", " ", self.selectorHost,self.selectorPort)
        self.maapiLocation      = self.config.maapiLocation

        self.timer_1            = dt.now()
        self.timer_2            = dt.now()
        self.timer_3            = dt.now()
        self.deviceList         = []
        self.libraryList        = []
        self.libraryList_id     = []
        self.runningServices    = []
        self.devicesGroupedBylib= {}
        self.localQueue         = {}
        self.libraryLastResponce= 10 # seconds
        self.socketServer       = SocketServer.SocketServer(self.objectname, self.queue, 1)
        self.socketServer.runTcpServer(self.selectorHost, self.selectorPort)
        self.maapilogger.log("INFO","Initialising Selector Module ")
        self.skippDev           = []
        self.pid                = os.getpid()
        self.sendingQueryToSocket = 0
        signal.signal(signal.SIGTERM, self.service_shutdown)
        signal.signal(signal.SIGINT, self.service_shutdown)


    def service_shutdown(self, signum, frame):
        self.maapilogger.log("INFO",f'Caught signal {signum} | stoping MaaPi {self.objectname}')
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
                    payload = self.helpers.pyloadToPicke(10, dev, self.deviceList, self.deviceListForRelated, self.selectorHost, self.selectorPort)
                    try:
                        for serv in self.runningServices:
                            if self.runningServices[serv]["ss_device_table_id"] == self.deviceList[dev]['dev_type_id']:

                                self.socketClient.sendStr(self.runningServices[serv]["ss_host"], self.runningServices[serv]["ss_port"], payload)

                                self.maapilogger.log("DEBUG",f"Devices sended to checkout readings {dev} | {self.deviceList[dev]['dev_user_name'].encode('utf-8').strip()} | {self.deviceList[dev]['dev_rom_id']}")
                                self.maapilogger.log("DEBUG",f"to {self.runningServices[serv]['ss_host']}:{self.runningServices[serv]['ss_port']}")

                    except Exception as e:
                        self.maapilogger.log("ERROR",f"Exception checkDbForOldreadings - Send dev_id: {dev} to lib: {self.deviceList[dev]['dev_type_id']} library for dev not exist in database for this location/board")
                        self.skippDev.append(dev)
                        self.localQueue[dev]=c_dev["dev_last_update"]



    def getDeviceList(self):
        gdstart = dt.now()

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

    def getRunningServices(self):
        """
        ss_device_table_id
        dodac do bazy danych pole id w maapi_running_socket_servers pole id !!!!!!!!!!

        """
        self.runningServices = self.maapiDB.table("maapi_running_socket_servers").get()


    def loop(self):
        while True:

            if (dt.now() - self.timer_3).seconds >= 60:
                self.skippDev = []
                self.getRunningServices()
                self.getDeviceList()
                self.timer_3 = dt.now()

            time.sleep(0.01)
            self.checkDbForOldreadings()
            self.responceToWatcher()


    def startConf(self):
        self.getRunningServices()
        self.maapilogger.log("INFO","Preparing to start Selector module")
        self.getDeviceList()



if __name__ == "__main__":
    MaapiSel =  MaapiSelector()
    MaapiSel.startConf()
    time.sleep(2)
    MaapiSel.loop()
