
import copy
import lib_maapi_main_helpers as Helpers
import MaaPi_Config as Config
import lib_maapi_main_dbconn as Db_connection
import lib_maapi_main_socketClient as SocketClient
import lib_maapi_main_logger as MaapiLogger
import lib_maapi_main_queue as Queue
import subprocess
from datetime import datetime as dt


class serviceClass():
    def __init__(self):
        self.running = True
        self.objectname = ""
        self.interpreterVer = ""
        self.queue = Queue.Queue()
        self.helpers = Helpers.Helpers()
        self.maapiDB = Db_connection.MaaPiDBConnection()
        self.config = Config.MaapiVars()
        self.board_id = self.helpers.updateBoardLocation(
            self.config.maapiLocation,
            self.maapiDB.table("maapi_machine_locations").filters_eq(ml_enabled = True).get()
            )
        self.socketClient = SocketClient.socketClient()
        self.maapilogger = MaapiLogger.Logger()
        self.maapilogger.name = self.objectname
        self.selectorHost = self.config.selectorHost
        self.selectorPort = self.config.selectorPort
        self.watcherHost = self.config.watcherHost
        self.watcherPort = self.config.watcherPort
        self.selecorName = self.config.selectorName
        self.payload_StopUDP = "777_0_0_0"
        self.payload_StopTCP = self.helpers.pyloadToPicke(
            777,
            " ",
            " ",
            " ",
            self.watcherHost,
            self.watcherPort
            )
        self.payload_Status = self.helpers.pyloadToPicke(
            00,
            " ",
            " ",
            " ",
            self.watcherHost,
            self.watcherPort
            )

        self.servicePids = {}
        self.libraryPID = {}
        self.libraryList = []
        self.libraryLastResponce = 600 # seconds

    def stopServices(self, service_host, service_port):
        """stopServices"""
        running_services = self.maapiDB.table(
            "maapi_running_socket_servers"
            ).get()
        try:
            for rs in running_services:
                if running_services[rs]["ss_port"] == service_port:
                    if running_services[rs]["ss_type"] == "TCP":
                        self.socketClient.sendStr(
                            service_host,
                            service_port,
                            self.payload_StopTCP
                            )

                        self.maapilogger.log(
                            "STOP",
                            f"ServiceClass | Kill message sended via TCP "
                            f"{service_host}:{service_port}"
                            )
                    if running_services[rs]["ss_type"] == "UDP":
                        self.socketClient.sendViaUDP(
                            service_host,
                            service_port,
                            self.payload_StopUDP
                            )

                        self.maapilogger.log(
                            "STOP",
                            f"ServiceClass | Kill message sended via UDP "
                            f"{service_host}:{service_port}"
                            )
        except:
            self.maapilogger.log(
                "STOP",
                f"ServiceClass | Selector Service - Socket Server not running"
                )

    def stopServiceKillPID(self, pid_object):
        try:
            self.maapilogger.log("STOP", f"ServiceClass | Killing Service PID ")
            pid_object.kill()
        except:
            self.maapilogger.log("STOP", f"ServiceClass | Service - pid not exist")
        else:
            self.maapilogger.log("STOP", f"ServiceClass | Service - Process Killed")

    def startSelectorServices(self, host, port, name):
        try:
            self.maapilogger.log(
                "START",
                f"Starting Selector Service at host:{host}, port:{port}"
                )

            self.selectorPid = subprocess.Popen([self.interpreterVer, f"{name}.py"])

            self.maapilogger.log(
                "START",
                f"Selector Service started at PID: {self.selectorPid.pid}"
                )

            self.maapiDB.insertRaw(
                "maapi_running_py_scripts",(
                    "default",
                    f"'{name}'",
                    f"'{name}.py'",
                    "now()",
                    f"{self.board_id}",
                    f"{self.selectorPid.pid }"
                    )
                )
            self.maapilogger.log(
                "START",
                f"Selector Service added to running service table in database.")

        except Exception as e:
            self.maapilogger.log("ERROR", f"startSelectorService() | {e}")

    def getLibraryList(self):
        try:
            self.libraryList = self.maapiDB.table(
                "maapi_device_list"
                ).filters_eq(
                    device_enabled=True,
                    device_location_id=self.board_id
                ).get()
            for ids in self.libraryList:
                self.queue.prepareQueueDevList(ids)
            self.maapilogger.log("DEBUG", "Devices library list updated")
        except:
            pass

    def startAllLibraryDeamon(self):
        for lib in self.libraryList:
            if self.libraryList[lib]["device_location_id"] == self.board_id:
                try:
                    self.startLibraryDeamon(lib)
                except Exception as e :
                    self.maapilogger.log("ERROR", f"Error: startlibraryDeamon() {e}")

    def stopLibraryDeamon(self, lib_id):
        try:
            self.maapilogger.log("STOP", f"Killing library deamon {lib_id}")
            if self.libraryPID[lib_id]:
                try:
                    self.stopServices(
                        self.libraryPID[lib_id]["host"],
                        self.libraryPID[lib_id]["port"],
                        )

                    self.maapilogger.log(
                        "STOP",
                        f"ServiceClass | Kill message sended "
                        f"{self.libraryPID[lib_id]['host']}"
                        f":{self.libraryPID[lib_id]['port']}"
                        )
                except:
                    self.maapilogger.log(
                        "STOP",
                        f"ServiceClass | Selector Service - Socket Server not running"
                        )

                self.libraryPID[lib_id]["pid"].kill()
                try:
                    del self.libraryPID[lib_id]
                    self.maapiDB.deleteRow(
                        "maapi_running_py_scripts",
                        f"py_pid={self.libraryPID['pid'].pid}"
                        )


                except Exception as e:
                    self.maapilogger.log(
                        "ERROR",
                        "Error: stoplibraryDeamon() pid not exist in "
                        "libraryPID{exc}".format(exc = e)
                        )
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
                self.maapilogger.log(
                    "START",
                    f"Starting library deamon {self.libraryList[lib]['device_lib_name']}"
                    )
                lists =[
                    self.interpreterVer,
                    f"{self.libraryList[lib]['device_lib_name']}.py",
                    f"{self.selectorHost}",
                    f"{int(self.selectorPort)+int(self.libraryList[lib]['id'])}",
                    f"{lib}"
                    ]

                file_ = f"{self.libraryList[lib]['device_lib_name']}.py"
                pid = subprocess.Popen(lists)
                name = self.libraryList[lib]['device_lib_name']
                port = int(self.selectorPort)+int(self.libraryList[lib]['id'])

                self.libraryPID[lib] = {
                    "id": lib,
                    "name": name,
                    "pid": pid,
                    "host": self.selectorHost,
                    "port": port,
                    "lastResponce": dt.now(),
                    "sendedQuery": 0
                    }

                self.maapilogger.log(
                    "START",
                    f"Lib:{self.libraryPID[lib]['name']} "
                    f"pid:{self.libraryPID[lib]['pid'].pid}")
                self.maapiDB.insertRaw(
                    "maapi_running_py_scripts", (
                        "default",
                        f"'{name}'",
                        f"'{file_}'",
                        "now()",
                        f"{int(self.board_id)}",
                        f"{int(pid.pid)}"
                        )
                    )
        except Exception as e :
            self.maapilogger.log(
                "ERROR",
                "Exception: startLibraryDeamon() {exc}".format(exc = e)
                )
    def checkLibrarylist(self):
        for lib in self.libraryList:
            try:
                self.libraryPID[lib]
            except:
                self.startLibraryDeamon(lib)
        lib_temp = copy.copy(self.libraryPID)
        for lib in lib_temp:
            if self.libraryList:
                if lib not in self.libraryList:
                    self.stopLibraryDeamon(lib)


    def checkLibraryProcess(self):
        lib_temp = copy.copy(self.libraryPID)
        for lib in lib_temp:
            try:
                if (dt.now() - lib_temp[lib]["lastResponce"]).seconds > self.libraryLastResponce and self.libraryPID[lib]["sendedQuery"] < 5:
                    self.maapilogger.log(
                        "STATUS",
                        f"Sending query to Selector: is ok? "
                        f"{lib_temp[lib]['name']} {lib_temp[lib]['host']},"
                        f" {lib_temp[lib]['port']}"
                        )
                    payload = self.helpers.pyloadToPicke(
                        00, " ", " ", " ",
                        self.watcherHost, self.watcherPort
                        )
                    try:
                        self.maapilogger.log(
                            "DEBUG",
                            f"Query sended to {lib_temp[lib]['name']}"
                            f" {lib_temp[lib]['host']},"
                            f" {lib_temp[lib]['port']}"
                            )

                        self.libraryPID[lib]["sendedQuery"] += 1
                        self.libraryPID[lib]["lastResponce"] = dt.now()
                        self.socketClient.sendStr(
                            lib_temp[lib]["host"],
                            lib_temp[lib]["port"],
                            payload
                            )
                    except Exception as e :
                        self.maapilogger.log(
                            "STATUS",
                            f"Service not responce - RESTARTING  "
                            f"{lib_temp[lib]['name']} {lib_temp[lib]['host']}"
                            f", {lib_temp[lib]['port']} | error:{e}")
                        self.restartLibraryDeamon(lib)

                if self.libraryPID[lib]["sendedQuery"] >= 5:
                    self.maapilogger.log(
                        "STATUS",
                        f"Service not responce - 5 attempts - RESTARTING  "
                        f"{lib_temp[lib]['name']} {lib_temp[lib]['host']}, "
                        f"{lib_temp[lib]['port']}"
                        )
                    self.libraryPID[lib]["lastResponce"] = dt.now()
                    self.restartLibraryDeamon(lib)
            except Exception as error:
                self.maapilogger.log(
                    "ERROR",
                    f"Exception: checkLibraryProcess() {error}"
                    )


    def checkLibraryForObject(self, library, queue, queue_nr):
        try:
            for lib in library:
                self.maapilogger.log(
                    "DEBUG",
                    f"Checking Library for   {int(queue[queue_nr][5])} ="
                    f"=  {int(library[lib]['port'])}"
                    )
                if int(queue[queue_nr][5]) == int(library[lib]['port']):
                    return lib

            return False
        except EnvironmentError as error:
            self.maapilogger.log("ERROR", f"checkLibraryForObject {error}")

    def checkLibraryResponce(self):
        """Check library reponce in queue """
        try:
            lib_temp = copy.copy(self.libraryPID)
            while self.queue.getSocketStatusLen():
                queue_ = (self.queue.getSocketStatus())[self.objectname][self.watcherHost][self.watcherPort]
                self.maapilogger.log("DEBUG", f"Checking queue {queue_}")
                for nr in queue_:
                    lib = self.checkLibraryForObject(lib_temp, queue_, nr)

                    if lib:
                        self.libraryPID[lib]["sendedQuery"] = 0
                        self.libraryPID[lib]["lastResponce"] = dt.now()
                        self.maapilogger.log(
                            "STATUS",
                            f"Get Responce from {queue_[nr][4]} {queue_[nr][5]}"
                            )
                        self.maapiDB.updateRaw(
                            f"maapi_running_socket_servers ",
                            f" ss_last_responce = now() ",
                            f" ss_host='{lib_temp[lib]['host']}' and "
                            f"ss_port='{lib_temp[lib]['port']}'"
                            )
        except EnvironmentError as error:
            self.maapilogger.log("ERROR", f"checkLibraryResponce {error}")
