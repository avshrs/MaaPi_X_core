#!/usr/bin/python3.7
# -*- coding: utf-8 -*-import sys
###############################################################
#
#                          MAAPI X
#
##############################################################

class MaapiVars():

    def __init__(self):
        self.selectorName            = "MaaPi_Selector_5_0.py"

        self.watcherHost             = "127.0.0.1"
        self.watcherPort             = 55542
        self.selectorHost            = self.watcherHost
        self.selectorPort            = self.watcherPort + 1
        self.udpListenerPort         = 60000

        self.maapiLocation         ="SERV"
        self.maapiDbName           ='MaaPi'
        self.maapiDbUser           ='maapi_db'
        self.maapiDbHost           ='192.168.1.110'
        self.maapiDbpass           ='889192'



