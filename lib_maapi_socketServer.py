import socket
import lib_maapi_helpers as Helpers
from datetime import datetime as dt

class SocketServer():
    def __init__(self):
        self.helpers    = Helpers.Helpers()
        self.debug      = 1
        self.sock       = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    def __del__(self):
        self.sock.close()

    def _debug(self, level, msg):
        if self.debug >= level:
            print("DEBUG lib socketServer\t\t{0} {1}, {2}".format(level, dt.now(), msg))

    def startServer(self, owner, host, port, queue, object_id):
        try:
            try:
                self.sock.bind((host, int(port)))
            except:
                self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.sock.bind((host, int(port)))
            self.sock.listen(10000)
            self._debug(1,self.sock)

            while True:
                client, address = self.sock.accept()
                with client:
                    while True:
                        data = client.recv(2000000000)
                        if not data: break
                        id_, payload_, fromHost_, fromPort_ = self.helpers.payloadFromPicke(data)
                        if id_ == 0 :
                            client.send(bytes(0xff))
                        else:
                            queue.addSocketRadings(owner, host, port, id_, payload_, fromHost_, fromPort_)

        except EnvironmentError as  e:
            self._debug(1,"Except detect:")
            self._debug(1,"---------------------------------------------------")
            self._debug(1,"{e}".format(e=e))
            self._debug(1,"---------------------------------------------------")
            self.sock.close()
        finally:
            self.sock.close()


