#!/usr/bin/python3.7
# -*- coding: utf-8 -*-import sys
###############################################################
#
#                          MAAPI X
#
##############################################################
import lib_maapi_main_checkDevCond               as CheckDev
import lib_maapi_main_queue                      as Queue
import lib_maapi_main_logger                     as MaapiLogger
import lib_maapi_main_socketClient               as SocketClient
import lib_maapi_main_socketServer               as SocketServer
import lib_maapi_main_helpers                    as Helpers
import lib_maapi_main_dbORM                      as Db_connection
import lib_maapi_main_readings                   as Readings
import time, copy, sys, smbus, os, signal
from lim_maapi_i2c_bus import I2C_MaaPi
from statistics import median, stdev, mean

from datetime import datetime as dt
import subprocess

class PFC8591():
    def __init__(self,host,port,id_):
        self.queue              = Queue.Queue()
        self.objectname         = "PFC8591"
        self.host               = host
        self.port               = int(port)
        self.maapiCommandLine   = []
        self.timer_1            = dt.now()
        self.timer_2            = dt.now()
        self.maapilogger        = MaapiLogger.Logger()
        self.maapilogger.name   = self.objectname
        self.pfcTable           = []
        self.busOptionsTable    = []
        self.readings           = Readings.Readings(self.objectname,self.host, self.port)
        self.maapiDB            = Db_connection.MaaPiDBConnection()
        self.socketServer       = SocketServer.SocketServer(self.objectname, self.queue,1)
        self.socketServer.runTcpServer(self.host, self.port)
        self.bus                = I2C_MaaPi(1)
        self.pid                = os.getpid()
        self.writePid(self.pid)

        signal.signal(signal.SIGTERM, self.service_shutdown)
        signal.signal(signal.SIGINT, self.service_shutdown)

    def service_shutdown(self, signum, frame):
        self.maapilogger.log("INFO",f'Caught signal {signum} | stoping MaaPi {self.objectname}')
        self.writePid("")
        #self.socketServer.killServers()
        raise SystemExit


    def writePid(self, pid):
        f = open(f"pid/MaaPi_{self.objectname}.sens.pid", "w")
        f.write(f"{pid}")
        f.close()

    def checkQueueForReadings(self):
        self.readings.checkQueueForReadings(self.readValues, self.queue)


    def getTables(self):
        self.pfcTable = self.maapiDB.table("maapi_pfc8591").get()
        self.busOptionsTable = self.maapiDB.table("maaapi_bus_options").get()
        self.maapilogger.log("INFO","Update pfcTable and busOptionsTable from database")


    def readValues(self, que, dev_id, devices_db, devices_db_rel):
        self.maapilogger.log("INFO",f"Reading Values ")
        value = 0
        error = 0
        data  = []
        out   = []
        unit_id = devices_db[dev_id]['dev_unit_id']
        # 20 - V
        # 21 - A
        # 19 - W
        bus_options_addres = int(self.busOptionsTable[devices_db[dev_id]['dev_bus_options_id']]['bus_options'],16)
        bus_options_bus_id = self.busOptionsTable[devices_db[dev_id]['dev_bus_options_id']]['bus_id']
        for pfc in self.pfcTable:
            self.maapilogger.log("INFO",f"check dev {dev_id} |  {self.pfcTable[pfc]['pfc_address']} vs {bus_options_addres} and {self.pfcTable[pfc]['pfc_id']} vs {bus_options_bus_id}")
            if self.pfcTable[pfc]['pfc_address'] == bus_options_addres and  self.pfcTable[pfc]['pfc_id'] == bus_options_bus_id:
                print ("entered to inf pfc")
                address = bus_options_addres
                sens_nr = bus_options_bus_id
                ref_volt = self.pfcTable[pfc]['pfc_ref_voltage']
                middle = self.pfcTable[pfc]['pfc_middle_point']
                accuracy = self.pfcTable[pfc]['pfc_read_accuracy']
                toAmper = self.pfcTable[pfc]['pfc_to_amper']
                to_wats = self.pfcTable[pfc]['pfc_to_wats']
                to_volts = self.pfcTable[pfc]['pfc_to_volts']
                data = self.bus.write_read_i2c_block_data32(address,sens_nr,sens_nr,accuracy)
                for d in data:
                    out.append(abs(d - middle))
                value = (max(out)*(ref_volt/255))

                if unit_id == 21:
                    value = value / toAmper
                elif unit_id == 19:
                    value = (value / toAmper) * to_wats
                elif unit_id == 20:
                    vzlie = value * to_volts

        return value, error


    def loop(self):
        while True:
            if (dt.now() - self.timer_1).seconds >= 10:
                self.timer_1 = dt.now()
                self.getTables()
            time.sleep(0.01)
            self.checkQueueForReadings()

if __name__ == "__main__":
    PFC8591_ =  PFC8591(sys.argv[1],sys.argv[2],sys.argv[3])
    PFC8591_.getTables()
    PFC8591_.loop()




