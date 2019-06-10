#!/usr/bin/python3.6
#-*- coding: utf-8 -*-
###############################################################
#
#                          MAAPI X
#
##############################################################

from lib_maapi_sens_proto import SensProto
import time, copy, sys, os, signal
import RPi.GPIO as GPIO
from datetime import datetime as dt
import lib_maapi_main_gpio as gipoHelper

class GPIO_PI(SensProto):
    def __init__(self,host, port,id_):
        super().__init__()
        self.id_ = id_
        self.gpioHelper = gipoHelper.GPIOHelpers()
        self.objectname = "GPIO_PI"
        self.host = host
        self.timer_1 = dt.now()
        self.port = int(port)
        self.mp_table = []
        self.libInit()

    def updateTable(self):
        self.mp_table = self.maapiDB.table("maapi_switch").columns('switch_update_rom_id', "*").filters_eq(switch_enabled=True).get()


    def readValues(self, nr, dev_id, devices_db, devices_db_rel):
        value, error = 0, 0
        gpio_finale = 0
        target = self.mp_table[dev_id]["switch_update_rom_id"]
        source_dev = self.mp_table[dev_id]["switch_data_from_sens_id"]
        try:

            if source_dev and target:
                value = self.gpioHelper.gpio_condytion_checker(dev_id, self.mp_table)
                gpio_finale = self.gpioHelper.invertLogicState(dev_id, value)
                GPIO.setup(devices_db[dev_id]["dev_gpio_pin"], GPIO.OUT)
                if gpio_finale != 2:
                    if GPIO.input(devices_db[dev_id]["dev_gpio_pin"]):
                        if gpio_finale == 0:
                            GPIO.output(devices_db[dev_id]["dev_gpio_pin"], gpio_finale)
                        return gpio_finale, 0
                    else:
                        if gpio_finale == 1:
                            GPIO.output(devices_db[dev_id]["dev_gpio_pin"], gpio_finale)
                        return gpio_finale, 0
                else:
                    return GPIO.input(devices_db[dev_id]["dev_gpio_pin"]), 0
            else:
                return 0, 1
        except EnvironmentError as e:
             self.maapilogger.log("ERROR", f"Exception read values {self.objectname}: {e}")
             return 0, 1


    def service_startup(self):
        self.updateTable()
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

    def loop(self):
        while self.isRunning:
            time.sleep(0.1)
            self.checkQueueForReadings()
            self.responceToWatcher()
            if (dt.now() - self.timer_1).seconds >= 5:
                self.timer_1 = dt.now()
                self.updateTable()

if __name__ == "__main__":
    GPIO_PI_ =  GPIO_PI(sys.argv[1],sys.argv[2],sys.argv[3])
    GPIO_PI_.service_startup()
    GPIO_PI_.loop()
