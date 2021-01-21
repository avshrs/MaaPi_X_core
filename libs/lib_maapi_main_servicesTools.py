class ServiceTools():

   def startMaaPiServices(self):
        try:
            self.maapilogger.log("START", f"Starting MaaPi Service at host:{self.selectorHost}, port:{self.selectorPort}")
            self.selectorPid = subprocess.Popen([self.interpreterVer, f"{name}.py"])
            self.maapilogger.log("START", f"Selector Service started at PID: {self.selectorPid.pid}")
            self.maapiDB.insertRaw("maapi_running_py_scripts", ("default", "'Selector'", "'MaaPi_Selector.py'", "now()", f"{self.board_id}", f"{self.selectorPid.pid }" ))
            self.maapilogger.log("START", f"Selector Service added to running service table in database.")
            self.lastCheck = dt.now()
        except Exception as e:
            self.maapilogger.log("ERROR", f"startSelectorService() | {e}")


    def stopServiceViaTCP(self,service_host,service_port):
        try:
            payload_StopTCP    = self.helpers.pyloadToPicke(777, " ", " ", " ", self.watcherHost,self.watcherPort)
            self.maapilogger.log("STOP", f"Killing service via TCP Message")
            try:
                self.socketClient.sendStr(service_hostt,service_port, payload)
                self.maapilogger.log("STOP", f"Message sended")
            except:
                self.maapilogger.log("STOP", f"Selector Service - Socket Server not running")
            self.selectorPid.kill()
        except:
            self.maapilogger.log("STOP", f"Selector Service - not started")
        else:
            self.maapilogger.log("STOP", f"Selector Service - Process Killed")


    def restartSelectorService(self):
        self.maapilogger.log("STATUS", f"Restrting Selector Service")
        self.stopSelectorService()
        self.startSelectorService()


    def checkSelectorStatus(self):
        if (dt.now() - self.lastCheck).seconds > 60 and not self.checkSended:
            self.maapilogger.log("STATUS", f"Checking Selector status")
            try:
                self.maapilogger.log("STATUS", f"Sending Query to {self.selectorHost}, {self.selectorPort} for status")
                self.socketClient.sendStr(self.selectorHost, self.selectorPort, self.payload_Status)
                self.checkSended = True
                self.responceS == False
                self.SelectorResponce= dt.now()
                self.lastCheck= dt.now()
            except:
                self.maapilogger.log("STATUS", f"ERROR - Socket Server is not avalible {self.selectorHost}, {self.selectorPort} | Restarting")
                self.restartSelectorService()


    def responceFromSelector(self):
        if self.queue.getSocketStatusLen() > 0:
            queueTmp  = self.queue.getSocketStatus()
            queue_ = queueTmp[self.objectname][self.watcherHost][self.watcherPort]
            for nr in queue_:
                if queue_[nr][0] == 0xff:
                    self.maapilogger.log("STATUS", f"Get Responce from Selector")
                    self.checkSended = False
                    self.responceS == True
                if queue_[nr][0] == 777:
                    self.service_shutdown()