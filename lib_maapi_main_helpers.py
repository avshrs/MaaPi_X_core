#!/usr/bin/python3.7
# -*- coding: utf-8 -*-import sys
###############################################################
#
#                          MAAPI X
#
##############################################################
import pickle

class Helpers:
    def __init__(self):
        self.instructions = {
            "readFromDev_id" : 10,
            "readFromDev_rom_id" : 11,
            "recive_from_UDP" : 99,
        }

    def pyloadToPicke(self, message_id, payload, payload2, payload3, fromHost, fromPort):
        data = {"id":message_id,
                "payload":payload,
                "payload2":payload2,
                "payload3":payload3,
                "fromHost":fromHost,
                "fromPort":fromPort}
        return pickle.dumps(data)

    def payloadFromPicke(self, pickled):
        data = pickle.loads(pickled)
        return data["id"], data["payload"], data["payload2"], data["payload3"], data["fromHost"], data["fromPort"]

    def scanQueueForIncommingQuerys(self,queue, objectname, selectorHost, selectorPort):
        pass

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



    def to_sec(self, value, unit):
        _seconds = 0
        if unit == 2: _seconds = value * 60
        elif unit == 3: _seconds = value * 3600
        else: _seconds = value
        return _seconds
