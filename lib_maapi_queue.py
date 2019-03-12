#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
##############################################################
#
#                          MAAPI 5.0
#                           Queue
#
##############################################################

from collections import defaultdict
from datetime import datetime as dt
import logging


class Queue():
    def __init__(self):
        self.seqSRnr           = 0
        self.queue_tcp_radings = {}
        self.socketReadings    = {}
        self.debug             = 1

    def _debug(self, level, msg):
        if self.debug >= level:
            print("DEBUG lib socketServer\t\t{0} {1}, {2}".format(level, dt.now(), msg))


    def addSocketRadings(self, owner, fomHost, onPort, pyload_id ,data, reciveToHost = None, reciveToPort = None, dt_=dt.now()):
        if not self.socketReadings:
            data_ = [pyload_id, data, reciveToHost, reciveToPort, dt_]
            id_   = {}
            port_ = {}
            host_ = {}
            id_[self.seqSRnr] = data_
            port_[onPort]     = id_
            host_[fomHost]    = port_
            self.socketReadings[owner] = host_
            self._debug(1, "insert new data: {d}".format(d=self.socketReadings))
        else:
            self.socketReadings[owner][fomHost][onPort][self.seqSRnr] = [data, reciveToHost, reciveToPort, dt_]
            self._debug(1, "insert update data: {d}".format(d = self.socketReadings))
        self.seqSRnr += 1


    def getSocketRadings(self):
        return self.socketReadings


    def get_queue_nr(self):
         return self.queue_nr


    def set_queue_nr(self,nr):
        self.queue_nr = nr

    def get_tcp_radings(self):
        return self.queue_tcp_radings


    def set_tcp_radings(self, nr, dict_):
        if nr not in self.queue_tcp_radings:
            self.queue_tcp_radings[nr] = [dict_]
        else:
            self.queue_tcp_radings[nr] += [dict_]


    def __del__(self):
        pass