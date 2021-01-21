#!/usr/bin/python3.7
# -*- coding: utf-8 -*-import sys
###############################################################
#
#                          MAAPI X
#
##############################################################
import lib_maapi_main_helpers as Helpers
from datetime import datetime as dt, timedelta
import lib_maapi_main_logger as MaapiLogger


class CheckDevCond:
    def __init__(self):
        self.helpers = Helpers.Helpers()
        self.maapilogger = MaapiLogger.Logger()
        self.maapilogger.name = f"CheckDevCond"

    def conditionDeviceReferenceDev(self ,devices_db, devices_db_rel, dev_id, value, minmax):
        """Check condition from reference device"""
        collectValuesCond_bool = devices_db[dev_id][
            f'dev_collect_values_if_cond_{minmax}_e']

        collectValuesRef_value = devices_db_rel[devices_db[dev_id][
            'dev_collect_values_if_cond_from_dev_id']]['dev_value']

        collectValuesCond_value = devices_db[dev_id][
            f'dev_collect_values_if_cond_{minmax}']

        if collectValuesCond_bool:

            if minmax == "min":
                if collectValuesRef_value <= collectValuesCond_value:
                    condition = 1
                else:
                    condition = 0

            if minmax == "max":
                if collectValuesRef_value >= collectValuesCond_value:
                    condition = 1
                else:
                    condition = 0
        else:
            condition = -1
        return condition

    def conditionDevice(self, devices_db, dev_id, value, minmax):
        """Check condition on self readings"""
        try:
            collectValuesCond_bool = devices_db[dev_id][
                f'dev_collect_values_if_cond_{minmax}_e']

            collectValuesCond_value = devices_db[dev_id][
                f'dev_collect_values_if_cond_{minmax}']

            if collectValuesCond_bool:
                if minmax == "min":
                    if value <= collectValuesCond_value:
                        condition = 1
                    else:
                        condition = 0
                if minmax == "max":
                    if value >= collectValuesCond_value:
                        condition = 1
                    else:
                        condition = 0
            else:
                condition = -1
        except:
            condition = -1
        return condition


    def checkDevCond(self, devices_db, devices_db_rel, dev_id, value):
        """Check if dev can write to database"""
        cond_min = -1
        cond_max = -1
        cond_result = -1
        value_ = value
        boolean = True

        if devices_db[dev_id]['dev_collect_values_if_cond_e']:
            if devices_db[dev_id]['dev_collect_values_if_cond_from_dev_e'] and \
            devices_db[dev_id]['dev_collect_values_if_cond_from_dev_id']:

                ref_lastUpdate = devices_db_rel[devices_db[dev_id][
                    'dev_collect_values_if_cond_from_dev_id']]['dev_last_update']

                ref_interval = devices_db_rel[devices_db[dev_id][
                    'dev_collect_values_if_cond_from_dev_id']]['dev_interval']

                ref_intervalUnit = devices_db_rel[devices_db[dev_id][
                    'dev_collect_values_if_cond_from_dev_id']]['dev_interval_unit_id']

                ref_intervalSec = self.helpers.to_sec(ref_interval, ref_intervalUnit)

                if (dt.now() - ref_lastUpdate).seconds <= (ref_intervalSec * 2):
                    cond_min = self.conditionDeviceReferenceDev(
                        devices_db, devices_db_rel, dev_id, value, "min")

                    cond_max = self.conditionDeviceReferenceDev(
                        devices_db, devices_db_rel, dev_id, value, "max")
                else:
                    cond_max = -1
                    cond_min = -1
            else:
                cond_min = self.conditionDevice(devices_db, dev_id, value, "min")
                cond_max = self.conditionDevice(devices_db, dev_id, value, "max")

            if cond_max != -1 or cond_min != -1:
                if cond_max == 1 or cond_min == 1:

                    cond_result = 1
                else:
                    cond_result = 0
            else:
                cond_result = -1

            self.maapilogger.log(
                "DEBUG",
                f"Checking dev {dev_id} with value {value} - "
                f"cond_result = {cond_result}  "
                f"|cond_max={cond_max} | cond_min={cond_min}"
                )
        else:
            cond_result = -1

        if cond_result !=0:
            value_ = value
            boolean = True
        else:
            if devices_db[dev_id]['dev_collect_values_if_cond_force_value_e']:
                value_ = devices_db[dev_id]['dev_collect_values_if_cond_force_value']
                boolean = True
            else:
                value_ = value
                boolean = False

        if not devices_db[dev_id]['dev_collect_values_to_db']:
            boolean = False

        return value_, boolean
