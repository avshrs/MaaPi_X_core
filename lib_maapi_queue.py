#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
##############################################################
#
#                          MAAPI 5.0
#                           Queue
#
##############################################################
from datetime import datetime as dt
from threading import RLock


class queue():
    def __init__(self):
        self.seqSRnr = 0
        self.queue_tcp_radings = {}

        #self.socketReadings = {"owner": {"fomHost": {"onPort":[{id:["data","reciveTohost","reciveToPort"]]}}} }
        self.socketReadings = {}
        self.lock = RLock()

    def addSocketRadings(self,owner,fomHost,onPort, data, reciveToHost = None, reciveToPort = None, dt_=dt.now()):
        try:
            self.lock.acquire()
            if not self.socketReadings:
                data_=[data,reciveToHost,reciveToPort,dt_]
                id_={} 
                port_={}
                host_={}
                id_[self.seqSRnr]=data_
                port_[onPort]=id_
                host_[fomHost]=port_
                self.socketReadings[owner]=host_
                #print ("empty",self.socketReadings)
            else:
                self.socketReadings[owner][fomHost][onPort][self.seqSRnr]=[data,reciveToHost,reciveToPort,dt_]
                #print ("adding",self.socketReadings)
            self.seqSRnr +=1
        except:
            pass
        finally:
            self.lock.release()

    def getSocketRadings(self):
        try:
            self.lock.acquire()
            return self.socketReadings
        finally:
            self.lock.release()
    def get_queue_nr(self):
         return self.queue_nr

    def set_queue_nr(self,nr):
        self.queue_nr = nr

    def get_tcp_radings(self):
        return self.queue_tcp_radings   

    def set_tcp_radings(self,nr,dict_):
        if nr not in self.queue_tcp_radings:
            self.queue_tcp_radings[nr]=[dict_]
        else:
            self.queue_tcp_radings[nr]+=[dict_]  
       
    def __del__(self):
        pass