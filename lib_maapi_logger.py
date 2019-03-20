
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


class Logger():
    def __init__(self):
        self.defaultDebugLevel = 3
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
            print("MaaPi | {0:<20} | {1:^6} | {2:<16} | {3}".format(self.name, self.levels[level], time, msg))