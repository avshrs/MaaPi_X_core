#!/usr/bin/python3.7
# -*- coding: utf-8 -*-import sys
###############################################################
#
#                          MAAPI X
#
##############################################################
import time
import socket

class socketClient():
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def sendStrAndRecv(self,host,port, payload):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.send(payload)
            data = s.recv(1024)
            s.close()
        return data

    def sendStr(self,host,port, payload):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.send(payload)
            s.close()
