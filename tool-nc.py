#!/usr/bin/env python3
import time
import socket


HOST = "127.0.0.1" # The server's hostname or IP address 
PORT = 55551 # The port used by the server





with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(bytes("0,is ok?","utf-8"))
    data = s.recv(1024)
    print("50001 Received", repr(data))
