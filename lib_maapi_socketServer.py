import socket
from datetime import datetime as dt

class SocketServer():
    def __init__(self):
        self.debug = 1
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    def __del__(self):
        self.sock.close()

    def _debug(self, level, msg):
        if self.debug >= level:
            print("DEBUG lib socketServer\t\t{0} {1}, {2}".format(level, dt.now(), msg))


    def startServer(self,owner, host, port, queue, object_id):
        try:
            try:
                #self.sock  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.bind((host, int(port)))
            except:
                self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.sock.bind((host, int(port)))
            self.sock.listen(1000)  
            self._debug(1,self.sock)
            while True:
                client, address = self.sock.accept()
                with client:
                    while True:
                        data = client.recv(20000)
                        if not data: break
                        self._debug(1,"Data recived from {address} - data {data}".format(address=address,data=data))
                        data_ , ip_, port_ = data.decode("utf-8").split(",")
                       
                        queue.addSocketRadings(owner, host, port, data, ip_, port_)   
                        
                        if data_ =="is ok?":
                            response = bytes("{payload}".format(payload="ok"),"utf-8")
                            client.send(response)
                            self._debug(1,"Responce sended to {address} - data {response}".format(address=address, response=response) ) 

        except Exception as e :
            self._debug(1,"Except detect:")
            self._debug(1,"---------------------------------------------------")
            self._debug(1,"{e}".format(e=e))
            self._debug(1,"---------------------------------------------------")
            self.sock.close()

        finally:
            self.sock.close()
           
   
 
