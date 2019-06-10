
#!/usr/bin/python3.7
# -*- coding: utf-8 -*-
##############################################################
#
#                          MAAPI 5.0
#                          Readings
#
##############################################################
import logging
from datetime import datetime as dt
import lib_maapi_main_dbconn as Db_connection
import MaaPi_Config as Config
import os


logging.basicConfig(filename= f"{os.getcwd()}/log/MaaPi_logger.log", level = logging.DEBUG, format = '%(asctime)s - %(message)s', datefmt = '%m/%d/%Y %H:%M:%S')


class Logger():
    def __init__(self):
        self.config = Config.MaapiVars()
        self.maapiLocation = self.config.maapiLocation
        self.defaultDebugLevel = 7
        self.printable = self.config.debug
        self.maapiDB = Db_connection.MaaPiDBConnection()
        self.name = "logger"
        self.levels = {
            0: "OFF",
            1: "ERROR",
            2: "START",
            3: "STOP",
            4: "READ",
            5: "STATUS",
            6: "WARN",
            7: "INFO",
            8: "DEBUG",
            9: "ALL",
            "OFF": "OFF",
            "START": "START",
            "STOP": "STOP",
            "READ": "READ",
            "STATUS": "STATUS",
            "ERROR": "ERROR",
            "WARN": "WARN",
            "INFO": "INFO",
            "DEBUG": "DEBUG",
            "ALL": "ALL",
       }

        self.levelsPrior = {
            0: ("OFF"),
            1: ("OFF", "ERROR"),
            2: ("OFF", "ERROR", "START"),
            3: ("OFF", "ERROR", "START", "STOP"),
            4: ("OFF", "ERROR", "START", "STOP", "READ"),
            5: ("OFF", "ERROR", "START", "STOP", "READ", "STATUS"),
            6: ("OFF", "ERROR", "START", "STOP", "READ", "STATUS", "WARN"),
            7: ("OFF", "ERROR", "START", "STOP", "READ", "STATUS", "WARN", "INFO"),
            8: ("OFF", "ERROR", "START", "STOP", "READ", "STATUS", "WARN", "INFO", "DEBUG"),
            9: ("OFF", "ERROR", "START", "STOP", "READ", "STATUS", "WARN", "INFO", "DEBUG", "ALL")
       }

    def log(self, level, msg):
        try:
            if  self.levels[level] in self.levelsPrior[self.defaultDebugLevel]:
                time= "{0:0>2}:{1:0>2}:{2:0>2} - {3:0>6}".format(dt.now().hour,dt.now().minute,dt.now().second,dt.now().microsecond)
                msg_ = str(msg).replace("'","")
                msg__ = str(msg_).replace('\"', '')
                if self.printable:
                    print(f"MaaPi  |  {self.name:<17}  |  {level:^6}  |  {time:<16}  |  {msg}")
                logging.info(f"MaaPi  |  {self.name:<17}  |  {level:^6}  |  {time:<16}  |  {msg}")
                self.maapiDB.insertRaw("maapi_logs", ("default", f"'{level}'", f"'{self.name}'","now()",f"'{msg__}'", f"'{self.maapiLocation}'"))
                #self.maapiDB.clean_logs()
        except:
            pass

    def logPrintOnly(self, level, msg):
        try:
            if  self.levels[level] in self.levelsPrior[self.defaultDebugLevel]:

                time = "{0:0>2}:{1:0>2}:{2:0>2} - {3:0>6}".format(dt.now().hour,dt.now().minute,dt.now().second,dt.now().microsecond)

                msg_ = str(msg).replace("'","")
                msg__ = str(msg_).replace('\"', '')
                if self.printable == 1:
                    print(f"MaaPi  |  {self.name:<17}  |  {self.levels[level]:^6}  |  {time:<16}  |  {msg}")

        except:
            pass
