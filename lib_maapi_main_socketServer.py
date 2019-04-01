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
        self.sockUDP            = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.selfkill = False
        self.board_id           = self.helpers.updateBoardLocation(self.config.maapiLocation,self.maapiDB.table("maapi_machine_locations").filters_eq(ml_enabled = True).get())


    def startServerTCP(self, host, port):
        try:
            self.maapilogger.log("START",f"Adding {self.objectname} Socket to dataBase - Active Sockets List")
            pid = os.getpid()
            self.maapiDB.insertRaw("maapi_running_socket_servers", ("default",f"'{self.objectname}'",f"'{host}'",f"{port}","now()", f"{pid}",f"{self.board_id}","now()","'TCP'"))
            try:
                self.sockTCP.bind((host, port))
            except:
                # add loop with increasing port until its find free slot
                self.sockTCP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.sockTCP.bind((host, port))
            self.sockTCP.listen(10000)
            self.maapilogger.log("START",self.sockTCP)

            while True and not self.selfkill:
                client, address = self.sockTCP.accept()
                with client:
                    while True and not self.selfkill:
                        data = client.recv(200000)
                        if not data:
                            break

                        payload_id, payload_, payload2_, payload3_, fromHost_, fromPort_ = self.helpers.payloadFromPicke(data)
                        self.maapilogger.log("DEBUG",f"GET mesage id={payload_id}")
                        if payload_id == 10:
                            self.queue.addSocketRadings(self.objectname, host, port, payload_id, payload_, payload2_, payload3_ ,fromHost_, fromPort_)

                        elif payload_id == 0 or payload_id == 0xff:
                            self.queue.addSocketStatus(self.objectname, host, port, payload_id, payload_, payload2_, payload3_ ,fromHost_, fromPort_)


                        elif payload_id == 777 :
                            self.queue.addSocketStatus(self.objectname, host, port, payload_id, payload_, payload2_, payload3_ ,fromHost_, fromPort_)
                            self.maapilogger.log("STOP",f"Get Slef Kill instruction via SocketTCP")
                            time.sleep(1)
                            self.sockTCP.close()
                            self.joiningTCP()
        except Exception() as e:
            self.maapilogger.log("ERROR", f"Exception in startServerTCP {self.objectname}: {e}")

    def startServerUDP(self, host, port):
        try:
            self.maapiDB.insertRaw("maapi_running_socket_servers", ("default",f"'{self.objectname}'",f"'{host}'",f"{port}","now()", f"{pid}",f"{self.board_id}", "now()", "'UDP'"))
            self.sockUDP.bind((host, port))
            self.maapilogger.log("INFO",self.sockUDP)
            while True and not self.selfkill:
                if self.selfkill:
                    self.maapilogger.log("INFO",f"self.selfkill ==  {self.selfkill} - stopin UDP")
                    self.sockUDP.close()
                    self.joining()

                data, address = self.sockUDP.recvfrom(4096)
                if not data:
                    break

                payload_id, dev_id, value, name  = data.decode("utf-8").split("_")
                if int(payload_id) == 99:
                    self.queue.addSocketRadings(self.objectname, host, port, str(payload_id), int(dev_id), float(value), str(name) )

                elif int(payload_id) == 777 :
                    self.maapilogger.log("STOP",f"Get Slef Kill instruction via SocketUDP")
                    self.sockUDP.close()
                    self.joiningUDP()
                else:
                    self.maapilogger.log("INFO",f"Get unknown packet via udp")

        except Exception as e:
            self.maapilogger.log("ERROR", f"Exception in startServerUDP {self.objectname}: {e}")


    def runTcpServer(self, host, port):
        self.maapilogger.log("START",f"{self.objectname} Run TCP Server")
        self.threads["TCP"] = Thread(target=self.startServerTCP,args=(host, port))
        self.threads["TCP"].start()


    def runUdpServer(self, host, port):
        self.maapilogger.log("START","{0} Run UDP Server".format(self.objectname ))
        self.threads["UDP"] = Thread(target=self.startServerUDP, args=(host, port))
        self.threads["UDP"].start()

    def joiningTCP(self):
        self.selfkill = True
        try:
            self.maapilogger.log("STOP","socket TCP -  join thread")
            self.threads["TCP"].join()
        except:
            pass
    def joiningUDP(self):
        try:
            self.maapilogger.log("STOP","socket UTP -  join thread")
            self.threads["UDP"].join()
        except:
            pass