#!/usr/bin/python3.7
# -*- coding: utf-8 -*-import sys
###############################################################
#
#                          MAAPI X
#
##############################################################

from lib_maapi_sens_proto import SensProto
import time, copy, sys, os, signal

from datetime import datetime as dt


class MaaPiMath(SensProto):
    def __init__(self, host, port, id_):
        super().__init__()
        self.objectname = "MaaPiMath"
        self.id_ = id_
        self.host = host
        self.port = int(port)
        self.maapiMathTable = []
        self.timer_1 = dt.now()
        self.libInit()


    def checkForQueue(self):
        if self.queue.getSocketRadingsLen() > 0:
            queue_  = (self.queue.getSocketRadings())[self.owner][self.host][self.port]



    def loop(self):
        while True:
            if (dt.now() - self.timer_1).seconds >= 10:
                self.timer_1 = dt.now()

            time.sleep(0.01)
            self.responceToWatcher()



if __name__ == "__main__":
    MaaPiMath_ =  MaaPiMath(sys.argv[1], sys.argv[2], sys.argv[3])
    MaaPiMath_.service_startup()
    MaaPiMath_.loop()
