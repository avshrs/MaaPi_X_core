import sys
from datetime import datetime
import math
import lib.MaaPi_DB_connection as maapidb
from lib.lib_maapi_check import Check


class class_get_values(object):
    debug = 0

    @classmethod
    def _debug(self, level, msg):
        if self.debug >= level:
            print("DEBUG MATH EXP\t\t {0} {1}, {2}".format(level, datetime.now(), msg))

    @classmethod
    def get_values_and_count(self, math_id, maapi_math, maapi_devices):
        value = 0
        if maapi_math[math_id]['math_data_from_1_id']:
            V1 = v1 = maapi_devices[int(maapi_math[math_id]['math_data_from_1_id'])]['dev_value']
        else: V1 = v1 = 'none'

        if maapi_math[math_id]['math_data_from_2_id']:
            V2 = v2 = maapi_devices[int(maapi_math[math_id]['math_data_from_2_id'])]['dev_value']
        else: V2 = v2 = 'none'

        if maapi_math[math_id]['math_data_from_3_id']:
            V3 = v3 = maapi_devices[int(maapi_math[math_id]['math_data_from_3_id'])]['dev_value']
        else: V3 = v3 = 'none'

        if maapi_math[math_id]['math_data_from_4_id']:
            V4 = v4 = maapi_devices[int(maapi_math[math_id]['math_data_from_4_id'])]['dev_value']
        else: V4 = v4 = 'none'

        try:
            value = eval(maapi_math[math_id]["math_math"])
        except:
            maapidb.MaaPiDBConnection.insert_data(maapi_math[math_id]['math_update_rom_id'],0,' ',False)

        return value

    @classmethod
    def __init__(self,*args):
        maapi_devices = maapidb.MaaPiDBConnection().table("devices").columns('dev_id',
                                                                             'dev_rom_id',
                                                                             'dev_value',
                                                                             ).get()
        maapi_math = maapidb.MaaPiDBConnection().table("maapi_math").columns( 'id',
                                                                               'math_user_id',
                                                                               'math_name',
                                                                               'math_update_rom_id',
                                                                               'math_data_from_1_id',
                                                                               'math_data_from_2_id',
                                                                               'math_data_from_3_id',
                                                                               'math_data_from_4_id',
                                                                               'math_math',
                                                                               'math_descript',
                                                                               'math_enabled',
                                                                               ).get()
        for dev_id in args:
            for math_id in maapi_math:
                if int(dev_id[0]) == int(maapi_math[math_id]['math_update_rom_id']):
                    condition, condition_min_max, force_value  = Check().condition(dev_id[0])
                    self._debug(2,"Condition is = {0}\t condition_min_max is = {1}, \t forced value is = {2}".format(condition, condition_min_max, force_value))
                    if condition:
                        if condition_min_max:
                            value = self.get_values_and_count(math_id, maapi_math, maapi_devices)
                            maapidb.MaaPiDBConnection.insert_data(maapi_math[math_id]['math_update_rom_id'],value,' ',True)
                            self._debug(1,"Condition min_max = {2}  \t Read value from sensor id = {0}, value is ={1}".format(dev_id[0],value, condition_min_max))
                        else:
                            maapidb.MaaPiDBConnection.insert_data(dev_id[0],force_value,' ',True)
                            self._debug(1,"Forcing value for sensor id = {0} \t forced vslur is = {1} ".format(dev_id[0],force_value))
                    else:
                        value = self.get_values_and_count(math_id, maapi_math, maapi_devices)
                        maapidb.MaaPiDBConnection.insert_data(maapi_math[math_id]['math_update_rom_id'],value,' ',True)
                        self._debug(1,"Readed value for sensor id = {0}   is = {1} ".format(dev_id[0],value))