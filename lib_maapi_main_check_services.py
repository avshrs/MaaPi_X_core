import lib_maapi_main_logger        as MaapiLogger
import lib_maapi_main_socketClient  as SocketClient
import lib_maapi_main_helpers       as Helpers
import subprocess

class ServicesTools():
    def __init__(self):
        self.objectname         = "ServicesTools"
        self.maapilogger        = MaapiLogger.Logger()
        self.maapilogger.name   = self.objectname
        self.socketClient       = SocketClient.socketClient()
        self.maapiDB            = Db_connection.MaaPiDBConnection()
        self.helpers            = Helpers.Helpers()
        self.payload_StopTCP    = self.helpers.pyloadToPicke(777, " ", " ", " ", "xxx",0)
        self.payload_StopUDP    = "777_0_0_0"


    def startService(self, interpreter, boardId, name, host, port):
        try:
            self.maapilogger.log("START", f"Starting MaaPi Service at host:{host}, port:{port}")
            servicePid = subprocess.Popen([interpreter, f"{name}.py"])
            self.maapilogger.log("START", f"Selector Service started at PID: {servicePid.pid}")
            self.maapiDB.insertRaw("maapi_running_py_scripts", ("default", "'{name}'", "'{name}.py'", "now()", f"{boardId}", f"{servicePid.pid }" ))
            self.maapilogger.log("START", f"{name} Service added to running service table in database.")
            return servicePid
        except Exception as e:
            return 0
            self.maapilogger.log("ERROR", f"Start service Error - inter:{interpreter}, board:{boardId}, name:{name}, host:,{host}, port:{port}  | message {e}")


    def stopService(self, pid):
        try:
            self.maapilogger.log("STOP", f"Try to kill service: {pid.pid}")
            pid.kill()
        except Exception as e:
            self.maapilogger.log("STOP", f"Killing Service error pid:{pid.pid} | error message {e}")
        else:
            self.maapiDB.deleteRow("maapi_running_py_scripts", f"py_pid={pid.pid}")
            self.maapilogger.log("STOP", f"Stop Service - Process Killed {pid.pid}")

    def sendStopSocketService(self, host, port, messageType):
        try:
            if messageType == "TCP":
                self.socketClient.sendStr(host,port, self.payload_StopTCP)
                self.maapilogger.log("STOP",f"Sending Stop message to TCP Service {host} {port}")
            if messageType == "UDP":
                self.socketClient.sendViaUDP(host, port, bytes(self.payload_StopUDP.encode()))
                self.maapilogger.log("STOP",f"Sending Stop message to UDP Service {host} {port}")
        except Exception as e:
            self.maapilogger.log("STOP", f"Stop Socket | error message {e}")
            var = 150


    def sendStatusQuery(self, fromHost, fromPort, toHost, toPort):
        payload_Status = self.helpers.pyloadToPicke(00, " ", " ", " ", fromHost, fromPort)
        try:
            if messageType == "TCP":
                self.maapilogger.log("STATUS", f"Sending Query to {toHost}, {toPort} for status")
                self.socketClient.sendStr(toHost, toPort, self.payload_Status)
            return 1
        except Exception as e:
            self.maapilogger.log("STATUS", f"ERROR - Socket Server is not avalible {toHost}, {toPort} | error Message {e}")
            return 0

    def responceFromSelector(self, queue, host, port):
        if queue.getSocketStatusLen() > 0:
            queueTmp  = queue.getSocketStatus()
            queue_ = queueTmp[self.objectname][host][port]
            for nr in queue_:
                if queue_[nr][0] == 0xff:
                    self.maapilogger.log("STATUS", f"Get Responce from Selector")
                    self.checkSended = False
                    self.responceS == True
                if queue_[nr][0] == 777:
                    self.service_shutdown()