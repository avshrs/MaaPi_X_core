#!/usr/bin/python3.7
# -*- coding: utf-8 -*-import sys
###############################################################
#
#                          MAAPI X
#
##############################################################

import socket, sys
import lib_maapi_main_helpers        as Helpers
import lib_maapi_main_logger         as MaapiLogger
from datetime import datetime        as dt
from threading import Lock, Thread

class SocketServer():
    def __init__(self, objectname, queue, object_id):
        self.objectname         = objectname
        self.helpers            = Helpers.Helpers()
        self.maapilogger        = MaapiLogger.Logger()
        self.maapilogger.name   = "{0} Sock.".format(self.objectname )
        self.object_id          = object_id
        self.queue              = queue
        self.threadTcp          = []
        self.threadUdp          = []


    def __del__(self):
        self.thread[0].join()
        self.threadUdp[0].join()

    def startServerTCP(self, host, port):
        try:
            sockTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sockTCP.bind((host, int(port)+1))
            except:
                sockTCP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sockTCP.bind((host, int(port)+1))
            sockTCP.listen(10000)
            self.maapilogger.log("INFO",sockTCP)
            while True:
                client, address = sockTCP.accept()
                with client:
                    while True:
                        data = client.recv(200000)
                        if not data:
                            break
                        payload_id, payload_, payload2_, payload3_, fromHost_, fromPort_ = self.helpers.payloadFromPicke(data)
                        if payload_id == 0 :
                            client.send(bytes(0xff))
                        if payload_id !=0:
                            self.maapilogger.log("DEBUG",f"Get message from {fromHost_} {fromPort_} payload {payload_} payload {payload2_}")
                            self.queue.addSocketRadings(self.objectname, host, int(port)+1, payload_id, payload_, payload2_, payload3_ ,fromHost_, fromPort_)

        except Exception as e:
            self.maapilogger.log("ERROR",f"startServerTCP {e}")


    def startServerUDP(self, host, port):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sockUDP:
            sockUDP.bind((host, int(port)))
            self.maapilogger.log("INFO",sockUDP)
            while True:
                data, address = sockUDP.recvfrom(4096)
                if not data: break
                self.maapilogger.log("DEBUG",f"Udp data decoded {data.decode('utf-8')}")
                payload_id, dev_id, value, name  = data.decode("utf-8").split("_")
                if data:
                    if int(payload_id) == 99:
                        self.queue.addSocketRadings(self.objectname, host, port, str(payload_id), int(dev_id), float(value), str(name) )


    def runTcpServer(self, host, port):
        self.maapilogger.log("INFO","{0} Run TCP Server".format(self.objectname ))
        self.threadTcp.append(Thread(target=self.startServerTCP,args=(host, port)))
        self.threadTcp[0].start()


    def runUdpServer(self, host, port):
        self.maapilogger.log("INFO","{0} Run UDP Server".format(self.objectname ))
        self.threadUdp.append(Thread(target=self.startServerUDP, args=(host, port)))
        self.threadUdp[0].start()