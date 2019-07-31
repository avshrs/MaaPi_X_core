#!/usr/bin/python3.7
# -*- coding: utf-8 -*-import sys
###############################################################
#
#                          MAAPI X
#
##############################################################

import lib_maapi_main_checkDevCond as CheckDev
import lib_maapi_main_dbconn as Db_connection
import lib_maapi_main_logger as MaapiLogger
import lib_maapi_main_helpers as Helpers
from datetime import datetime as dt


class Readings:
    def __init__(self, owner, host, port):
        self.owner = owner
        self.checkDev = CheckDev.CheckDevCond()
        self.host = host
        self.port = port
        self.maapiDB = Db_connection.MaaPiDBConnection()
        self.maapilogger = MaapiLogger.Logger()
        self.maapilogger.name = f"Read - {self.owner}"
        self.helpers = Helpers.Helpers()


    def checkQueueForReadings(self, method, queue):
        dev = 0
        try:
            if queue.getSocketRadingsLen() > 0:
                queue_ = (queue.getSocketRadings())[self.owner][self.host][self.port]
                value, error = 0, 0
                for nr in queue_:
                    dev_id = queue_[nr][1]
                    dev = queue_[nr][1]
                    devices_db = queue_[nr][2]
                    devices_db_rel = queue_[nr][3]
                    if queue_[nr][0] == self.helpers.instructions["readFromDev_id"]:
                        try:
                            startd = dt.now()
                            value, error = method(nr, dev_id, devices_db, devices_db_rel)

                            stopd = dt.now()
                            if isinstance(value, float):
                                val = round(float(value),3)
                            else:
                                val = value

                            self.maapilogger.log(
                                "READ",
                                f"Readed  id: {dev_id:<10} |  "
                                f"DevID: {dev_id:<5} |  "
                                f"Name: {devices_db[dev_id]['dev_user_name']:<25} |  "
                                f"Value: {val:<15} | inTime: {(stopd-startd)}")

                            self.insertReadingsToDB(
                                nr,
                                float(value),
                                dev_id,
                                devices_db,
                                devices_db_rel,
                                error
                                )

                        except EnvironmentError as e:
                            value = 0
                            error = 2

                            self.maapilogger.log(
                                "ERROR",
                                f"Error while reading values from "
                                f"{dev_id} - {devices_db[dev_id]['dev_user_name']}"
                                f": {e}")

                            self.insertReadingsToDB(
                                nr,
                                value,
                                dev_id,
                                devices_db,
                                devices_db_rel,
                                error
                                )


        except EnvironmentError as e :
            self.maapilogger.log("ERROR",f"checkQueueForReadings | {dev} | {e}")

    def insertReadingsToDB(self, nr, readed_value, dev_id, devices_db, devices_db_rel,  error_code):
        try:
            if error_code > 0:
                codes={
                    0: "reading ok",
                    1: "device not exist",
                    2: "error while reading"
                    }

                self.maapilogger.log("ERROR",f"Error in reading method - error code: {codes[error_code]}")
                self.maapiDB.insert_readings(dev_id,float(f"9999.{error_code}")," ",False)
            else:
                value, boolean = self.checkDev.checkDevCond( devices_db, devices_db_rel, dev_id, readed_value)
                self.maapilogger.log("READ","Insert readings to DataBase")
                self.maapiDB.insert_readings(dev_id,value," ",boolean)

        except EnvironmentError as e:
            self.maapilogger.log("ERROR",f"Error inserting data from CMD: {e}")
            try:
                self.maapiDB.insert_readings(dev_id,0," ",False)
            except:
                pass