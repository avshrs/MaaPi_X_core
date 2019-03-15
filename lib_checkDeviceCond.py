import lib_maapi_helpers                    as Helpers
from datetime import datetime               as dt, timedelta


class CheckDevCond:
    def __init__(self):
        self.helpers = Helpers.Helpers()

    def conditionDeviceReferenceDev(self,devices_db, dev_id, value, minmax):
        collectValuesCond_bool      = devices_db[dev_id]['dev_collect_values_if_cond_{mm}_e'.format(mm=minmax)]
        collectValuesCond_value     = devices_db[dev_id]['dev_collect_values_if_cond_{mm}'.format(mm=minmax)]
        collectValuesRef_bool       = devices_db[devices_db[dev_id]['dev_collect_values_if_cond_from_dev_id']]['dev_value']
        collectValuesRef_value      = devices_db[devices_db[dev_id]['dev_collect_values_if_cond_from_dev_id']]['dev_value']

        if collectValuesCond_bool and collectValuesCond_value:
            if minmax =="min":
                if collectValuesRef_bool <= collectValuesRef_value:
                    condition = 1
                else:
                    condition = 0
            if minmax =="max":
                if collectValuesRef_bool >= collectValuesRef_value:
                    condition = 1
                else:
                    condition = 0
        else:
            condition = -1
        return condition


    def conditionDevice(self,devices_db, dev_id, value, minmax):
        collectValuesCond_bool      = devices_db[dev_id]['dev_collect_values_if_cond_{mm}_e'.format(mm=minmax)]
        collectValuesCond_value     = devices_db[dev_id]['dev_collect_values_if_cond_{mm}'.format(mm=minmax)]

        if collectValuesCond_bool and collectValuesCond_value:
            if minmax =="min":
                if value <= collectValuesCond_value:
                    condition = 1
                else:
                    condition = 0
            if minmax =="max":
                if value >= collectValuesCond_value:
                    condition = 1
                else:
                    condition = 0
        else:
            condition = -1
        return condition


    def checkDevCond(self, devices_db, dev_id, value):
        cond_min = -1
        cond_max = -1
        cond_result = -1
        value_ = value
        boolean = True

        if devices_db[dev_id]['dev_collect_values_if_cond_e']:
            if devices_db[dev_id]['dev_collect_values_if_cond_from_dev_e'] and devices_db[dev_id]['dev_collect_values_if_cond_from_dev_id']:
                ref_lastUpdate      = devices_db[devices_db[dev_id]['dev_collect_values_if_cond_from_dev_id']]['dev_last_update']
                ref_interval      = devices_db[devices_db[dev_id]['dev_collect_values_if_cond_from_dev_id']]['dev_interval']
                ref_intervalUnit = devices_db[devices_db[dev_id]['dev_collect_values_if_cond_from_dev_id']]['dev_interval_unit_id']
                ref_intervalSec = self.helpers.to_sec(ref_interval, ref_intervalUnit)
                print (ref_lastUpdate)
                if (dt.now()- ref_lastUpdate).seconds <= (ref_intervalSec * 2):
                    cond_min = self.conditionDeviceReferenceDev(devices_db, dev_id, value, "min")
                    cond_max = self.conditionDeviceReferenceDev(devices_db, dev_id, value, "max")
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


