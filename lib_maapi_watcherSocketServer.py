import socket


class WatcherSocketServer():
    def startServer(self, host, port, queue, object_id):
        queue_ = queue
        try:
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
                print (client)
                with client:
                    while True:
                        data = client.recv(20000)
                        if not data: break
                        
                        queue_.set_tcp_radings(object_id,data)
                        response = data # ack ok
                        client.send(response)
        except Exception as e :
             print ("Except detect:\n---------------------------------------------------\n{0}".format(e))
             print ("---------------------------------------------------")

        finally:
            sock.close()
 