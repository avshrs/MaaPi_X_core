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
import lib_maapi_logger          as MaapiLogger



class Queue():
    def __init__(self):
        self.seqSRnr            = 0
        self.queue_tcp_radings  = {}
        self.socketReadings     = {}
        self.queueDevList       = {}
        self.maapilogger        = MaapiLogger.Logger()
        self.maapilogger.name   = "Queue"

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
            self.maapilogger.log("DEBUG", "insert new data: {d}".format(d=self.socketReadings))
        else:
            self.socketReadings[owner][fomHost][onPort][self.seqSRnr] = [data, reciveToHost, reciveToPort, dt_]
            self.maapilogger.log("DEBUG", "insert update data: {d}".format(d = self.socketReadings))
        self.seqSRnr += 1


    def getSocketRadings(self):
        return self.socketReadings




    def getQueueDevList(self):
        return self.queueDevList

    def rmFromQueueDevList(self,lib_id,dev_id):
        self.queueDevList[lib_id].remove(dev_id)

    def updateQueueDevList(self,lib_id,dev_id):
        try:
            if dev_id not in self.queueDevList[lib_id]:
                self.queueDevList[lib_id].append(dev_id)
        except Exception as e:
            self.maapilogger.log("ERROR","Devices - missing library of bad library id's  {Ex}".format(Ex=e))

    def prepareQueueDevList(self,lib_id):
        try:
            if self.queueDevList[lib_id]:
                pass
        except:
            self.queueDevList[lib_id]=[]
            self.maapilogger.log("DEBUG","Adding library id's do queue list {libb}".format(libb=lib_id))


    def get_tcp_radings(self):
        return self.queue_tcp_radings


    def set_tcp_radings(self, nr, dict_):
        if nr not in self.queue_tcp_radings:
            self.queue_tcp_radings[nr] = [dict_]
        else:
            self.queue_tcp_radings[nr] += [dict_]


    def __del__(self):
        pass