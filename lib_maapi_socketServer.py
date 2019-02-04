import socket
from datetime import datetime as dt

class SocketServer():
    def __init__(self):
        self.debug = 1
     
    def _debug(self, level, msg):
        if self.debug >= level:
            print("DEBUG lib socketServer\t\t\t{0} {1}, {2}".format(level, dt.now(), msg))


    def startServer(self,owner, host, port, queue, object_id):
        queue_=queue
        
        self._debug(1,"ss start")
        try:
            self._debug(1,"ss starttry ")
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind((host, int(port)))
            except:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind((host, int(port)))
            sock.listen(1000)  
            self._debug(1,sock)
            while True:
                client, address = sock.accept()
                with client:
                    while True:
                        data = client.recv(20000)
                        if not data: break
                        data, ip_, port_ = data.decode("utf-8").split(",")
                        queue_.addSocketRadings(owner, host, port, data, ip_, port_)         
                        #response = data # ack ok
                        #client.send(response)
        except Exception as e :
             self._debug(1,"Except detect:\n---------------------------------------------------\n{0}".format(e))
             self._debug(1,"---------------------------------------------------")
             sock.close()

        finally:
            sock.close()
           
   
 
