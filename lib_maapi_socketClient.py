#!/usr/bin/env python3
import time
import socket

class socketClient():
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def sendStr(self,host,port, payload):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(bytes("{payload}".format(payload=payload),"utf-8"))
            data = s.recv(1024)
        return data
