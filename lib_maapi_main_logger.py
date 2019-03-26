
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
import lib_maapi_main_dbORM                 as Db_connection
import MaaPi_Config                          as Config

import os

pwd =os.getcwd()

logging.basicConfig(
    filename=f'{pwd}/log/Maapi_logger.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%m/%d/%Y %H:%M:%S')



class Logger():
    def __init__(self):
        self.config              = Config.MaapiVars()
        self.maapiLocation      = self.config.maapiLocation
        self.defaultDebugLevel  = 3
        self.printable          = 0
        self.maapiDB            = Db_connection.MaaPiDBConnection()
        self.name = "logger"
        self.levels={ 0:"OFF", 1:"ERROR", 2:"WARN", 3:"INFO", 4:"DEBUG", 5:"ALL",
            "OFF":"OFF", "ERROR":"ERROR", "WARN":"WARN", "INFO":"INFO", "DEBUG":"DEBUG", "ALL":"ALL",
       }

        self.levelsPrior={ 0:("OFF"),
                           1:("OFF", "ERROR"),
                           2:("OFF", "ERROR", "WARN"),
                           3:("OFF", "ERROR", "WARN","INFO"),
                           4:("OFF", "ERROR", "WARN","INFO","DEBUG"),
                           5:("OFF", "ERROR", "WARN","INFO","DEBUG","ALL")
       }

    def log(self, level, msg):
        if  self.levels[level] in self.levelsPrior[self.defaultDebugLevel]:
            time= "{0:0>2}:{1:0>2}:{2:0>2} - {3:0>6}".format(dt.now().hour,dt.now().minute,dt.now().second,dt.now().microsecond)
            msg_ = msg.replace("'","")
            #msg = msg_.replace()
            self.maapiDB.insertRaw("maapi_logs", ("default", f"'{level}'", f"'{self.name}'","now()",f"'{msg_}'", f"'{self.maapiLocation}'"))

            if self.printable == 1:
                print(f"MaaPi  |  {self.name:<17}  |  {self.levels[level]:^6}  |  {time:<16}  |  {msg}")

            if self.levels[level] == "INFO":
                logging.info( f"\t| {self.name:<16} | {msg}")
            elif self.levels[level] == "DEBUG":
                logging.debug(f"\t| {self.name:<16} | {msg}")
            elif self.levels[level] == "ERROR":
                logging.error(f"\t| {self.name:<16} | {msg}")
            elif self.levels[level] == "EXCEPT":
                logging.exception(f"\t| {self.name:<16} | {msg}")