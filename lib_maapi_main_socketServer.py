#!/usr/bin/python3.7
# -*- coding: utf-8 -*-import sys
###############################################################
#
#                          MAAPI X
#
##############################################################

import socket, sys, os, signal
import lib_maapi_main_helpers        as Helpers
import lib_maapi_main_logger         as MaapiLogger
import lib_maapi_main_dbORM          as Db_connection
from datetime import datetime        as dt
from threading import Lock, Thread

class SocketServer():
    def __init__(self, objectname, queue, object_id):
        self.objectname         = objectname
        self.helpers            = Helpers.Helpers()
        self.maapilogger        = MaapiLogger.Logger()
        self.maapilogger.name   = f"{self.objectname }Sock."
        self.object_id          = object_id
        self.maapiDB            = Db_connection.MaaPiDBConnection()
        self.queue              = queue
        self.threads            = {}
        self.pid                = os.getpid()
        self.writePid(self.pid)
        self.sockTCP            = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        signal.signal(signal.SIGTERM, self.service_shutdown)
        signal.signal(signal.SIGINT, self.service_shutdown)

    def service_shutdown(self, signum, frame):
        self.maapilogger.log("INFO",f'Caught signal {signum} | stoping MaaPi SocetServer')

    def writePid(self, pid):
        f = open(f"pid/MaaPi_{self.objectname}.socket.pid", "w")
        f.write(f"{pid}")
        f.close()


    def startServerTCP(self, host, port):
        self.maapiDB.insertRaw("maapi_running_socket_servers", ("default",f"'{self.objectname}'",f"'{host}'",f"{port}"))
        # (id serial, ss_name text, ss_host text, ss_port int);
        try:

            try:
                self.sockTCP.bind((host, port))
            except:
                self.sockTCP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.sockTCP.bind((host, port))
            self.sockTCP.listen(10000)
            self.maapilogger.log("INFO",self.sockTCP)
            while True:
                client, address = self.sockTCP.accept()
                with client:
                    while True:
                        data = client.recv(200000)
                        if not data:
                            break
                        payload_id, payload_, payload2_, payload3_, fromHost_, fromPort_ = self.helpers.payloadFromPicke(data)
                        if payload_id == 0 :
                            client.send(bytes(0xff))
                        elif payload_id == 99 :
                            print ("Raise systemExit ----------------------------------------")
                            self.sockTCP.close()
                            raise SystemExit
                        else:
                            self.maapilogger.log("DEBUG",f"Get message from {fromHost_} {fromPort_} payload {payload_} payload {payload2_}")
                            self.queue.addSocketRadings(self.objectname, host, port, payload_id, payload_, payload2_, payload3_ ,fromHost_, fromPort_)

        except Exception as e:
            self.maapilogger.log("ERROR",f"startServerTCP {e}")


    def startServerUDP(self, host, port):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sockUDP:
            sockUDP.bind((host, port))
            self.maapilogger.log("INFO",sockUDP)
            while True:
                data, address = sockUDP.recvfrom(4096)
                if not data: break
                self.maapilogger.log("DEBUG",f"Udp data decoded {data.decode('utf-8')}")
                payload_id, dev_id, value, name  = data.decode("utf-8").split("_")
                if data:
                    if int(payload_id) == 99:
                        self.queue.addSocketRadings(self.objectname, host, port, str(payload_id), int(dev_id), float(value), str(name) )

    def killServers(self):
        self.sockTCP.close()
        for i in self.threads:
            print (f"run join {self.objectname }")
            self.threads[i].join()
            print (f"thread joined {self.objectname }")
        raise SystemExit

    def runTcpServer(self, host, port):
        self.maapilogger.log("INFO","{0} Run TCP Server".format(self.objectname ))
        self.threads["TCP"] = Thread(target=self.startServerTCP,args=(host, port))
        self.threads["TCP"].start()


    def runUdpServer(self, host, port):
        self.maapilogger.log("INFO","{0} Run UDP Server".format(self.objectname ))
        self.threads["UDP"] = Thread(target=self.startServerUDP, args=(host, port))
        self.threads["UDP"].start()

