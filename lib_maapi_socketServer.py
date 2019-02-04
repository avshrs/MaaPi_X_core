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
                with client:
                    while True:
                        data = client.recv(20000)
                        if not data: break
                        data, ip_, port_ = data.decode("utf-8").split(",")
                        queue_.addSocketRadings(owner, host, port, data, ip_, port_)         
                        #response = data # ack ok
                        #client.send(response)
        except Exception as e :
             print ("Except detect:\n---------------------------------------------------\n{0}".format(e))
             print ("---------------------------------------------------")
             sock.close()

        finally:
            sock.close()
           
   
 
