import socket
import lib_maapi_helpers        as Helpers
from datetime import datetime   as dt
import lib_maapi_logger         as MaapiLogger
from threading import Lock, Thread

class SocketServer():
    def __init__(self, objectname, host, port, queue, object_id):
        self.objectname         = objectname
        self.helpers            = Helpers.Helpers()
        self.sock               = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.maapilogger        = MaapiLogger.Logger()
        self.maapilogger.name   = "{0} Socket".format(self.objectname )

        self.host               = host
        self.port              = port
        self.object_id          = object_id
        self.queue              = queue
        self.thread             = []

    def __del__(self):
        #self.sock.close()
        #self.thread[0].join()
        pass

    def startServer(self):
        try:
            try:
                self.sock.bind((self.host, int(self.port)))
            except:
                self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.sock.bind((host, int(port)))
            self.sock.listen(10000)
            self.maapilogger.log("INFO",self.sock)
            while True:
                client, address = self.sock.accept()
                with client:
                    while True:
                        data = client.recv(200000)
                        if not data: break
                        id_, payload_, fromHost_, fromPort_ = self.helpers.payloadFromPicke(data)
                        if id_ == 0 :
                            client.send(bytes(0xff))
                        if id_ !=0:
                            self.maapilogger.log("DEBUG",f"Get message from {fromHost_} {fromPort_} payload {payload_}")
                            self.queue.addSocketRadings(self.objectname, self.host, self.port, id_, payload_, fromHost_, fromPort_)

        except EnvironmentError as  e:
            self.maapilogger.log("ERROR","Except detect:")
            self.maapilogger.log("ERROR","---------------------------------------------------")
            self.maapilogger.log("ERROR","{e}".format(e=e))
            self.maapilogger.log("ERROR","---------------------------------------------------")
            self.sock.close()
        finally:
            self.sock.close()


    def runTcpServer(self):
        self.maapilogger.log("INFO"," {0} Run TCP Server".format(self.objectname ))
        self.thread.append(Thread(target=self.startServer))
        self.thread[0].start()

