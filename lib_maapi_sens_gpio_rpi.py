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


class GPIO_PI(SensProto):
    def __init__(self,host,port,id_):
        super().__init__()
        self.id_ = id_
        self.objectname = "GPIO_PI"
        self.host = host
        self.timer_1 = dt.now()
        self.port = int(port)
        self.mp_table = []
        self.libInit()

    def updateTable(self):
        self.mp_table = self.maapiDB.table("maapi_switch").columns('switch_update_rom_id', "*").filters_eq(switch_enabled=True).get()

    def invert_state(self, sensID, gpio_val):
        if self.mp_table[sensID]["switch_invert"]:
            if gpio_val:
                gpio_finale = 0
            else:
                gpio_finale = 1
        else:
            gpio_finale = gpio_val
        return gpio_finale

    def getSourceHistory(self, dev, range_, min_max):
        counter = 0
        source_id = self.mp_table[dev][f"switch_data_from_sens_id"]
        source_history_values = self.maapiDB.select_last_nr_of_values(source_id, range_)
        for i in source_history_values:
            if min_max == "min":
                if i < self.mp_table[dev][f"switch_value_{min_max}"]:
                    counter += 1
            if min_max == "max":
                if i > self.mp_table[dev][f"switch_value_{min_max}"]:
                    counter += 1
        return self.checkConditionState(dev, counter)

    def getReferenceHistory(self, dev, range_, min_max):
        counter = 0
        ref_dev = self.mp_table[dev][f"switch_reference_sensor_{min_max}_id"]
        source_id = self.mp_table[dev][f"switch_data_from_sens_id"]
        source_history_values = self.maapiDB.select_last_nr_of_values(source_id, range_)
        device_range_value_ref = self.maapiDB.select_last_nr_of_values(ref_dev, range_)
        for i, ii in zip(device_range_value_ref, source_history_values):
            if min_max == "min":
                if ii < i + self.mp_table[dev][f"switch_value_{min_max}"]:
                    counter += 1
            if min_max == "max":
                if ii > i + self.mp_table[dev][f"switch_value_{min_max}"]:
                    counter += 1
        return self.checkConditionState(dev, counter)

    def checkConditionState(self, dev, counter):
        value = 0
        if self.mp_table[dev]["switch_range_acc"] == counter:
            # all readings match condition set to 1
            value = 1
        elif counter == 0:
            # all readings not match condition set to 0
            value = 0
        else:
            # some readings match condition set to 2
            value = 2
        return value


    def gpio_condytion_checker(self, sensID):
        result = {"min": 0, "max": 0}
        value = 0
        for min_max in ("min", "max"):
            if self.mp_table[sensID][f"switch_reference_sensor_{min_max}_e"]:
                result[min_max] = self.getReferenceHistory(sensID, self.mp_table[sensID]["switch_range_acc"], min_max)
            elif self.mp_table[sensID][f"switch_value_{min_max}_e"]:
                result[min_max] = self.getSourceHistory(sensID, self.mp_table[sensID]["switch_range_acc"], min_max)
        if result["min"] == 1 or result["max"] == 1:
            value = 1
        elif result["min"] == 2 or result["max"] == 2:
            value = 2
        self.maapilogger.log("INFO", f"gpio_condytion_checker return {value}")
        return value

    def readValues(self, que, dev_id, devices_db, devices_db_rel):
        value, error = 0, 0
        gpio_finale = 0
        target = self.mp_table[dev_id]["switch_update_rom_id"]
        source_dev = self.mp_table[dev_id]["switch_data_from_sens_id"]
        try:

            if source_dev and target:
                self.maapilogger.log("INFO", f"source_dev and target: {source_dev} and  {target}")
                value = self.gpio_condytion_checker(dev_id)
                self.maapilogger.log("INFO", f"gpio condition checker {value}")
                gpio_finale = self.invert_state(dev_id, value)
                self.maapilogger.log("INFO", f"inverted? {gpio_finale}")
                GPIO.setup(devices_db[dev_id]["dev_gpio_pin"], GPIO.OUT)
                if gpio_finale != 2:
                    self.maapilogger.log("INFO", f"gpio_finale != 2 True")
                    if GPIO.input(devices_db[dev_id]["dev_gpio_pin"]):
                        if gpio_finale == 0:
                            self.maapilogger.log("INFO", f"gpio_finale == 0 True")
                            GPIO.output(devices_db[dev_id]["dev_gpio_pin"], gpio_finale)
                            self.maapilogger.log("READ",f"set gpio to {gpio_finale}")
                        return gpio_finale, 0

                    else:
                        if gpio_finale == 1:
                            GPIO.output(devices_db[dev_id]["dev_gpio_pin"], gpio_finale)
                            self.maapilogger.log("READ",f"set gpio to {gpio_finale}")
                        return gpio_finale, 0
                else:
                    return (self.maapiDB.select_last_nr_of_values(dev_id, 1)), 0
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
