import lib_maapi_main_dbconn as Db_connection

class GPIOHelpers:
    def __init__(self):
        self.maapiDB = Db_connection.MaaPiDBConnection()


    def invertLogicState(self, sensID, value, true):
        if value == 1 or value == True:
            return 0
        elif value == 0 or value == False:
            return 1
        else:
            return value

    def getDeviceHistory(self, dev, dev_range, table,  min_max):
        counter = 0
        source_id = table[dev][f"switch_data_from_sens_id"]
        source_history_values = self.maapiDB.select_last_nr_of_values(source_id, dev_range)

        for i in source_history_values:
            if min_max == "min":
                if i < table[dev][f"switch_value_{min_max}"]:
                    counter += 1
            if min_max == "max":
                if i > table[dev][f"switch_value_{min_max}"]:
                    counter += 1

        return dev, counter

    def getDeviceAndReferDeviceHistory(self, dev, dev_range, table,  min_max):
        counter = 0
        refence_dev = table[dev][f"switch_reference_sensor_{min_max}_id"]
        source_dev = table[dev][f"switch_data_from_sens_id"]
        source_history_values = self.maapiDB.select_last_nr_of_values(source_dev, dev_range)
        device_dev_rangevalue_ref = self.maapiDB.select_last_nr_of_values(refence_dev, dev_range)

        for i, ii in zip(device_dev_rangevalue_ref, source_history_values):
            if min_max == "min":
                if ii < i + table[dev][f"switch_value_{min_max}"]:
                    counter += 1
            if min_max == "max":
                if ii > i + table[dev][f"switch_value_{min_max}"]:
                    counter += 1

        return dev, counter

    def checkConditionState(self, dev, counter, table):
        value = 0
        if table[dev]["switch_dev_rangeacc"] == counter:
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
            if table[sensID][f"switch_reference_sensor_{min_max}_e"]:
                result[min_max] = self.getReferenceHistory(sensID, table[sensID]["switch_dev_rangeacc"], min_max)
            elif table[sensID][f"switch_value_{min_max}_e"]:
                result[min_max] = self.getSourceHistory(sensID, table[sensID]["switch_dev_rangeacc"], min_max)
        if result["min"] == 1 or result["max"] == 1:
            value = 1
        elif result["min"] == 2 or result["max"] == 2:
            value = 2
        return value