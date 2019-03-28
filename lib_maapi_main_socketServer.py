#!/usr/bin/python3.7
# -*- coding: utf-8 -*-import sys
###############################################################
#
#                          MAAPI X
#
##############################################################

import socket, sys, os, signal, time
import lib_maapi_main_helpers        as Helpers
import lib_maapi_main_logger         as MaapiLogger
import lib_maapi_main_dbORM          as Db_connection
import MaaPi_Config                   as Config

from datetime import datetime        as dt
from threading import Lock, Thread

class SocketServer():
    def __init__(self, objectname, queue, object_id):
        self.objectname         = objectname
        self.config              = Config.MaapiVars()
        self.helpers            = Helpers.Helpers()
        self.maapilogger        = MaapiLogger.Logger()
        self.maapilogger.name   = f"{self.objectname }Sock."
        self.object_id          = object_id
        self.maapiDB            = Db_connection.MaaPiDBConnection()
        self.maapiLocation      = self.config.maapiLocation

        self.queue              = queue
        self.threads            = {}
        self.pid                = os.getpid()
        self.sockTCP            = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.selfkill = False
        self.board_location = self.maapiDB.table("maapi_machine_locations").filters_eq(ml_enabled = True).get()
        self.board_id = 77
        for i in self.board_location:
            if self.board_location[i]["ml_location"] == self.maapiLocation:
                self.board_id = self.board_location[i]["id"]


    def startServerTCP(self, host, port):
        try:
            self.maapilogger.log("DEBUG",f"Adding {self.objectname} Socket to dataBase - Active Sockets List")
            pid = os.getpid()
            self.maapiDB.insertRaw("maapi_running_socket_servers", ("default",f"'{self.objectname}'",f"'{host}'",f"{port}","now()", f"{pid}",f"{self.board_id}"))
            try:
                self.sockTCP.bind((host, port))
            except:
                self.sockTCP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.sockTCP.bind((host, port))
            self.sockTCP.listen(10000)
            self.maapilogger.log("INFO",self.sockTCP)

            while True and not self.selfkill:
                client, address = self.sockTCP.accept()
                with client:
                    while True and not self.selfkill:
                        data = client.recv(200000)
                        if not data:
                            break
                        payload_id, payload_, payload2_, payload3_, fromHost_, fromPort_ = self.helpers.payloadFromPicke(data)

                        if payload_id == 0 :
                            client.send(bytes(0xff))

                        elif payload_id == 777 :
                            self.maapilogger.log("INFO",f"Get Slef Kill instruction via Socket")
                            self.sockTCP.close()
                            self.joining()
                            self.selfkill = True
                        else:
                            self.maapilogger.log("DEBUG",f"Get message from {fromHost_} {fromPort_} payload {payload_} payload {payload2_}")
                            self.queue.addSocketRadings(self.objectname, host, port, payload_id, payload_, payload2_, payload3_ ,fromHost_, fromPort_)
        except Exception() as e:
            self.maapilogger.log("ERROR", f"Exception in startServerTCP {self.objectname}: {e}")

    def startServerUDP(self, host, port):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sockUDP:
            sockUDP.bind((host, port))
            self.maapilogger.log("INFO",sockUDP)

            while True and not self.selfkill:
                if self.selfkill:
                    self.maapilogger.log("INFO",f"self.selfkill ==  {self.selfkill} - stopin UDP")
                    self.sockUDP.close()
                    self.joining()
                    break

                data, address = sockUDP.recvfrom(4096)
                if not data:
                    break
                self.maapilogger.log("DEBUG",f"Udp data decoded {data.decode('utf-8')}")
                payload_id, dev_id, value, name  = data.decode("utf-8").split("_")

                if data:
                    if int(payload_id) == 99:
                        self.queue.addSocketRadings(self.objectname, host, port, str(payload_id), int(dev_id), float(value), str(name) )


    def runTcpServer(self, host, port):
        self.maapilogger.log("INFO",f"{self.objectname} Run TCP Server")
        self.threads["TCP"] = Thread(target=self.startServerTCP,args=(host, port))
        self.threads["TCP"].start()


    def runUdpServer(self, host, port):
        self.maapilogger.log("INFO","{0} Run UDP Server".format(self.objectname ))
        self.threads["UDP"] = Thread(target=self.startServerUDP, args=(host, port))
        self.threads["UDP"].start()

    def joining(self):
        try:
            self.threads["TCP"].join()
            self.maapilogger.log("INFO","socket TCP -  join thread")
        except:
            pass
        try:
            self.threads["UDP"].join()
            self.maapilogger.log("INFO","socket UTP -  join thread")
        except:
            pass