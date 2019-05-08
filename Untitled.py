import lib_maapi_main_dbORM                      as Db_connection


class MaapiSelector():
    def __init__(self):
        self.maapiDB            = Db_connection.MaaPiDBConnection()

    def getDeviceList(self):
        deviceList = self.maapiDB.table("devices").columns("dev_id","dev_rom_id").order_by('dev_id').get()

        for i in deviceList:
            rom = deviceList[i]["dev_rom_id"].replace("-", "_")
            strin = f"maapi_dev_rom_{rom}_values"
            print(strin)
            self.maapiDB.reindexTable(strin)


if __name__ == "__main__":
    MaapiSel =  MaapiSelector()
    MaapiSel.getDeviceList()