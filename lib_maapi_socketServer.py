import socket


class SocketServer():
    def startServer(self,owner, host, port, queue, object_id):
        queue_=queue
        print ("ss start")
        try:
            print ("ss starttry ")
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind((host, int(port)))
            except:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind((host, int(port)))
            
            sock.listen(1000)  
            print (sock)

            while True:
                client, address = sock.accept()
                ip_, port_ = client.getpeername()
                with client:
                    while True:
                        data = client.recv(20000)
                        if not data: break
                        queue_.addSocketRadings(owner, host, port, data, ip_, port_)         

                        queue_.set_tcp_radings(object_id,data)
                        if data.decode("utf-8").split(",")[0] == "0" and data.decode("utf-8").split(",")[1]=="is ok?":
                            response = bytes("ok","utf-8") # ack ok
                            client.send(response)
                        else:
                            response = data
                            client.send(response)
        except Exception as e :
             print ("Except detect:\n---------------------------------------------------\n{0}".format(e))
             print ("---------------------------------------------------")
             sock.close()

        finally:
            sock.close()
           
   
 
