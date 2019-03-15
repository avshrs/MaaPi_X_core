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



"""
id  name            type            decrtiption
------------------------------------------------------------------------
00  status          string - "ok"   recive status information

10  getReadings     list - id's     read data from sensor

20  putDataDB       dict id:value   put readings to dataBase
"""