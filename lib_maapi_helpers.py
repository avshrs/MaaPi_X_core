import pickle

class Helpers:
    def __init__(self):
        self.instructions = {
            "readFromDev_id" : 10,
            "readFromDev_rom_id" : 11,
        }



    def pyloadToPicke(self, message_id, payload, fromHost, fromPort):
        data = {"id":message_id,
                "payload":payload,
                "fromHost":fromHost,
                "fromPort":fromPort}
        return pickle.dumps(data)

    def payloadFromPicke(self, pickled):
        data = pickle.loads(pickled)
        return data["id"], data["payload"], data["fromHost"], data["fromPort"]


    def scanQueueForIncommingQuerys(self,queue, objectname, selectorHost, selectorPort):
        try:
            queue__= copy.deepcopy(queue[objectname][selectorHost][selectorPort])
        except:
            pass
        else:
            for que in queue__:
                id_       = queue__[que][0]
                data_     = queue__[que][1]
                recvHost_ = queue__[que][2]
                recvPort_ = queue__[que][3]
                dtime_    = queue__[que][4]

                if id_ == self.instructions["readFromDev_id"]:
                    del queue[objectname][selectorHost][selectorPort][que]

    def to_sec(self, value, unit):
        _seconds = 0
        if unit == 2: _seconds = value * 60
        elif unit == 3: _seconds = value * 3600
        else: _seconds = value
        return _seconds

    def checkConditionMin(self, device_list, dev_id, value):
        if device_list[dev_id]["dev_collect_values_if_cond_min_e"]:
            print ("min true")
            if device_list[dev_id]["dev_collect_values_if_cond_from_dev_e"]:
                print ("enable from dev")
                d_timeStamp = device_list[device_list[dev_id]["dev_collect_values_if_cond_from_dev_id"]]["dev_last_update"]
                d_interval = device_list[device_list[dev_id]["dev_collect_values_if_cond_from_dev_id"]]["dev_interval"]
                d_interval_unit = device_list[device_list[dev_id]["dev_collect_values_if_cond_from_dev_id"]]["dev_interval_unit_id"]
                d_value = device_list[device_list[dev_id]["dev_collect_values_if_cond_from_dev_id"]]["dev_value"]
                if (dt.now() - dev_rel_timeStamp).seconds > (self.to_sec(dev_rel_interval,dev_rel_interval_unit)*2):
                    if value < d_value - device_list[dev_id]["dev_collect_values_if_cond_min"]
                    return value
                else:
                    return
            else:
                if value < device_list[dev_id]["dev_collect_values_if_cond_min"]
                return true

    def checkCondition(self, device_list, dev_id, value):
        if device_list[dev_id]["dev_collect_values_if_cond_e"]:
            if device_list[dev_id]["dev_collect_values_if_cond_min_e"]:
            print ("dupa2")
                if device_list[dev_id]["dev_collect_values_if_cond_from_dev_e"]:
                    print ("dupa3")
                    dev_rel_timeStamp = device_list[device_list[dev_id]["dev_collect_values_if_cond_from_dev_id"]]["dev_last_update"]
                    dev_rel_interval = device_list[device_list[dev_id]["dev_collect_values_if_cond_from_dev_id"]]["dev_interval"]
                    dev_rel_interval_unit = device_list[device_list[dev_id]["dev_collect_values_if_cond_from_dev_id"]]["dev_interval_unit_id"]
                    if (dt.now() - dev_rel_timeStamp).seconds >  self.to_sec(dev_rel_interval,dev_rel_interval_unit):
                        print ("dupa4")
                else:
                    pass
            elif device_list[dev_id]["dev_collect_values_if_cond_max_e"]:
                print ("dupa5")
        else:
            print (value)
"""
                "dev_id",
                "dev_type_id",
                "dev_rom_id",
                "dev_bus_type_id",
                "dev_last_update",
                "dev_interval",
                "dev_interval_unit_id",
                "dev_interval_queue",
                "dev_machine_location_id",
                "dev_collect_values_if_cond_e",
                "dev_collect_values_if_cond_min_e",
                "dev_collect_values_if_cond_max_e",
                "dev_collect_values_if_cond_max",
                "dev_collect_values_if_cond_min",
                "dev_collect_values_if_cond_from_dev_e",
                "dev_collect_values_if_cond_from_dev_id",
                "dev_collect_values_if_cond_force_value_e",
                "dev_collect_values_if_cond_force_value",

id  name            type            decrtiption
------------------------------------------------------------------------
00  status          string - "ok"   recive status information

10  getReadings     list - id's     read data from sensor

20  putDataDB       dict id:value   put readings to dataBase
"""