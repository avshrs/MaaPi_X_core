#!/usr/bin/python3.7
# -*- coding: utf-8 -*-import sys
###############################################################
#
#                          MAAPI X
#
##############################################################

from collections import defaultdict
import queue
from datetime import datetime as dt
import lib_maapi_main_logger          as MaapiLogger
import copy
from threading import Lock, Thread
lock = Lock()


class Queue():
    def __init__(self):
        self.seqSRnr            = 0
        self.queue_tcp_radings  = {}
        self.socketReadings     = queue.Queue()
        self.queueDevList       = {}
        self.maapilogger        = MaapiLogger.Logger()
        self.add                = 0


    def addSocketRadings(self, owner, fomHost, onPort, payload_id, payload, payload2, payload3, reciveToHost = None, reciveToPort = None, dateTime=dt.now()):
        self.maapilogger.name   = f"Queue {owner}"
        ids  = {}
        port = {}
        host = {}
        ow   = {}
        pickledData = [payload_id, payload, payload2, payload3, reciveToHost, reciveToPort, dateTime]
        ids[self.seqSRnr] = pickledData
        port[onPort]     = ids
        host[fomHost]    = port
        ow[owner]        = host
        self.socketReadings.put(ow)
        self.maapilogger.log("DEBUG", "Insert new data to queue")
        self.seqSRnr += 1


    def getSocketRadings(self):
        return self.socketReadings.get()


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