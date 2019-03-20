#!/usr/bin/python3.7
# -*- coding: utf-8 -*-import sys
###############################################################
#
#                          MAAPI X
#
##############################################################

import lib_maapi_main_checkDevCond               as CheckDev
import lib_maapi_main_dbORM                      as Db_connection
import lib_maapi_main_logger                     as MaapiLogger
import lib_maapi_main_helpers                    as Helpers


class Readings:
    def __init__(self, owner, host, port):
        self.owner      =        owner
        self.host               = host
        self.port               = port
        self.maapiDB            = Db_connection.MaaPiDBConnection()
        self.maapilogger        = MaapiLogger.Logger()
        self.maapilogger.name   = f"Read - {self.owner}"
        self.helpers            = Helpers.Helpers()


    def checkQueueForReadings(self, method, queue):
        try:
            queueTmp  = queue.getSocketRadings()
            queue_ = queueTmp[self.owner][self.host][self.port]
            for nr in queue_:
                dev_id          = queue_[nr][1]
                devices_db      = queue_[nr][2]
                devices_db_rel  = queue_[nr][3]

                if queue_[nr][0] == self.helpers.instructions["readFromDev_id"]:
                    self.maapilogger.log("DEBUG",f"Device {dev_id} will be readed")
                    try:
                        value, error = method(nr, dev_id, devices_db, devices_db_rel)
                        self.maapilogger.log("INFO",f"Readed id: {nr:<10} DevID: {dev_id:<8} Name: {devices_db[dev_id]['dev_user_name']:<20} \tValue: {float(value)} ")
                    except Exception as e:
                        value = 0
                        error = 2
                        self.maapilogger.log("ERROR",f"Error while reading values: {e}")
                        self.insertReadingsToDB(nr ,value, dev_id, devices_db, devices_db_rel, error)
        except Exception as e :
            self.maapilogger.log("ERROR",f"{e}")

    def insertReadingsToDB(self, nr, readed_value, dev_id, devices_db, devices_db_rel,  error_code):
        try:
            if error_code > 0:
                #9999.0 reading ok
                #9999.1 device not exist
                #9999.2 error while reading
                self.maapilogger.log("DEBUG","Error while reading ")
                self.maapiDB.insert_readings(dev_id,float(f"9999.{error_code}"," ",False))
            else:
                value, boolean = self.checkDev.checkDevCond( devices_db, devices_db_rel, dev_id, readed_value)
                self.maapilogger.log("DEBUG","Insert readings to DataBase")
                self.maapiDB.insert_readings(dev_id,value," ",boolean)
        except EnvironmentError as e:
            self.maapilogger.log("ERROR",f"Error reading data from CMD: {e}")
            self.maapiDB.insert_readings(dev_id,0," ",False)
