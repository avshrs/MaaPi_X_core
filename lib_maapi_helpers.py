import pickle

class Helpers:
    def pyloadToPicke(self, message_id, payload, fromHost, fromPort):
        data = {"id":message_id,
                "payload":payload,
                "fromHost":fromHost,
                "fromPort":fromPort}
        return pickle.dumps(data)

    def payloadFromPicke(self, pickled):
        data = pickle.loads(pickled)
        return data["id"], data["payload"], data["fromHost"], data["fromPort"]
