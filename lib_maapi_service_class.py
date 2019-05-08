
import copy
import lib_maapi_main_helpers        as Helpers
import MaaPi_Config                   as Config
import lib_maapi_main_dbORM          as Db_connection
import lib_maapi_main_socketClient  as SocketClient
import lib_maapi_main_socketServer  as SocketServer
import lib_maapi_main_logger        as MaapiLogger
import lib_maapi_main_queue         as Queue
import subprocess
from datetime import datetime as dt


class serviceClass():
    def __init__(self):

        self.queue              = Queue.Queue()
        self.helpers            = Helpers.Helpers()
        self.maapiDB            = Db_connection.MaaPiDBConnection()
        self.config              = Config.MaapiVars()
        self.board_id           = self.helpers.updateBoardLocation(self.config.maapiLocation,self.maapiDB.table("maapi_machine_locations").filters_eq(ml_enabled = True).get())
        self.socketClient       = SocketClient.socketClient()
        self.maapilogger        = MaapiLogger.Logger()
        self.maapilogger.name   = self.objectname
        self.servicePids        = {}
        self.libraryPID         = {}
        self.libraryList        = []
        self.libraryLastResponce= 120 # seconds
        self.sendingQueryToSocket = 0



    def stopServiceViaTCP(self,service_host,service_port):
        self.maapilogger.log("STOP", f"ServiceClass | Killing service via TCP Message {service_host}:{service_port}")
        payload_StopTCP = self.helpers.pyloadToPicke(777, " ", " ", " ", service_host ,service_port)
        try:
            self.socketClient.sendStr(service_host,service_port, payload_StopTCP)
            self.maapilogger.log("STOP", f"ServiceClass | Kill message sended {service_host}:{service_port}")
        except:
            self.maapilogger.log("STOP", f"ServiceClass | Selector Service - Socket Server not running")


    def stopServiceKillPID(self,pid_object):
        try:
            self.maapilogger.log("STOP", f"ServiceClass | Killing Service PID ")
            pid_object.kill()
        except:
            self.maapilogger.log("STOP", f"ServiceClass | Service - pid not exist")
        else:
            self.maapilogger.log("STOP", f"ServiceClass | Service - Process Killed")

    def startSelectorServices(self, host, port, name):
        try:
            self.maapilogger.log("START", f"Starting Selector Service at host:{host}, port:{port}")
            self.selectorPid = subprocess.Popen([self.interpreterVer, f"{name}.py"])
            self.maapilogger.log("START", f"Selector Service started at PID: {self.selectorPid.pid}")
            self.maapiDB.insertRaw("maapi_running_py_scripts", ("default", f"'{name}'", f"'{name}.py'", "now()", f"{self.board_id}", f"{self.selectorPid.pid }" ))
            self.maapilogger.log("START", f"Selector Service added to running service table in database.")
            self.lastCheck = dt.now()
        except Exception as e:
            self.maapilogger.log("ERROR", f"startSelectorService() | {e}")

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def getLibraryList(self):
        self.libraryList = self.maapiDB.table("maapi_device_list").filters_eq(device_enabled = True, device_location_id = self.board_id).get()
        for ids in self.libraryList:
            self.queue.prepareQueueDevList(ids)
        self.maapilogger.log("DEBUG","Devices library list updated")


    def startAllLibraryDeamon(self):
          for lib in self.libraryList:
            if self.libraryList[lib]["device_location_id"] == self.board_id:
                try:
                    self.startLibraryDeamon(lib)
                except Exception as e :
                    self.maapilogger.log("ERROR", "Error: startlibraryDeamon() {exc}".format(exc = e))


    def stopLibraryDeamon(self, lib_id):
        try:
            self.maapilogger.log("STOP", f"Killing library deamon {lib_id}")
            if self.libraryPID[lib_id]:
                self.libraryPID[lib_id]["pid"].kill()
                try:
                    del self.libraryPID[lib_id]
                except Exception as e:
                    self.maapilogger.log("ERROR", "Error: stoplibraryDeamon() pid not exist in libraryPID{exc}".format(exc = e))
        except Exception as e:
            self.maapilogger.log("ERROR", f"library {lib_id} not exist in library libraryPID ")

    def restartLibraryDeamon(self, lib_id):
        try:
            self.stopLibraryDeamon(lib_id)
            self.startLibraryDeamon(lib_id)
        except Exception as e:
            self.maapilogger.log("ERROR", "Error: restartLibraryDeamon() {exc}".format(exc = e))


    def startLibraryDeamon(self, lib):
        try:
            if lib not in self.libraryPID and self.running:
                self.maapilogger.log("START", f"Starting library deamon {self.libraryList[lib]['device_lib_name']}")
                lists =[self.interpreterVer, f"{self.libraryList[lib]['device_lib_name']}.py", f"{self.selectorHost}",
                        f"{int(self.selectorPort)+int(self.libraryList[lib]['id'])}", f"{lib}"]

                file_=f"{self.libraryList[lib]['device_lib_name']}.py"
                pid = subprocess.Popen(lists)
                name = self.libraryList[lib]['device_lib_name']
                port = int(self.selectorPort)+int(self.libraryList[lib]['id'])

                self.libraryPID[lib] = {"id" : lib,  "name" : name,  "pid"  : pid,
                                        "host" : self.selectorHost,   "port" : port,   "lastResponce":dt.now(), "sendedQuery":0}

                self.maapilogger.log("START", f"Lib:{self.libraryPID[lib]['name']} pid:{self.libraryPID[lib]['pid'].pid}")
                self.maapiDB.insertRaw("maapi_running_py_scripts", ("default",
                                                                    f"'{name}'",
                                                                    f"'{file_}'",
                                                                    "now()",
                                                                    f"{int(self.board_id)}",
                                                                    f"{int(pid.pid)}"))

        except Exception as e :
            self.maapilogger.log("ERROR", "Exception: startLibraryDeamon() {exc}".format(exc = e))



# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def checkLibraryProcess(self):
        lib_temp = copy.copy(self.libraryPID)
        for lib in lib_temp:
            if lib in self.libraryList:
                try:
                    if (dt.now() - lib_temp[lib]["lastResponce"]).seconds > self.libraryLastResponce and self.libraryPID[lib]["sendedQuery"] < 3:
                        self.maapilogger.log("STATUS", f"Sending query to Selector: is ok? {lib_temp[lib]['name']} {lib_temp[lib]['host']}, {lib_temp[lib]['port']}")
                        payload = self.helpers.pyloadToPicke(00, " ", " ", " ",self.watcherHost,self.watcherPort)
                        try:
                            self.socketClient.sendStr(lib_temp[lib]["host"], lib_temp[lib]["port"], payload)
                            self.maapilogger.log("DEBUG", f"Query sended to {lib_temp[lib]['name']} {lib_temp[lib]['host']}, {lib_temp[lib]['port']}")
                            self.libraryPID[lib]["sendedQuery"] += 1
                            self.libraryPID[lib]["lastResponce"] = dt.now()
                        except:
                            self.maapilogger.log("STATUS", f"Service not responce - RESTARTING  {lib_temp[lib]['name']} {lib_temp[lib]['host']}, {lib_temp[lib]['port']}")
                            self.restartLibraryDeamon(lib)
                    elif self.libraryPID[lib]["sendedQuery"] >= 3:
                        self.libraryPID[lib]["lastResponce"] = dt.now()
                        self.maapilogger.log("STATUS", f"Service not responce - RESTARTING  {lib_temp[lib]['name']} {lib_temp[lib]['host']}, {lib_temp[lib]['port']}")
                        self.restartLibraryDeamon(lib)
                except Exception as e :
                    self.maapilogger.log("ERROR", "Exception: checkLibraryProcess() {exc}".format(exc = e))
            else:
                self.stopLibraryDeamon(lib)

    def checkLibraryResponce(self):
        lib_temp = copy.copy(self.libraryPID)
        if self.queue.getSocketStatusLen() > 0:
            queue_ = (self.queue.getSocketStatus())[self.objectname][self.watcherHost][self.watcherPort]
            for nr in queue_:
                for lib in lib_temp:
                    if int(queue_[nr][5]) == int(lib_temp[lib]['port']):
                        self.libraryPID[lib]["sendedQuery"] = 0
                        self.libraryPID[lib]["lastResponce"] = dt.now()
                        self.maapilogger.log("STATUS", f"Get Responce from {queue_[nr][4]} {queue_[nr][5]}")
                        self.maapiDB.updateRaw("maapi_running_socket_servers ", " ss_last_responce = now() ", f" ss_host='{lib_temp[lib]['host']}' and ss_port='{lib_temp[lib]['port']}'")
                    