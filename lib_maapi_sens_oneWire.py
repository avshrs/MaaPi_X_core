
#!/usr/bin/python
import sys, os
from datetime import datetime
import lib.MaaPi_DB_connection as maapidb
from lib.lib_maapi_check import Check
import logging

logging.basicConfig(
    filename='/home/pi/MaaPi110/bin/logs/Maapi_Selector.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%m/%d/%Y %H:%M:%S')


class class_get_values(object):
    debug = 0

    @classmethod
    def _debug(self, level, msg):
        if self.debug >= level:
            logging.debug("lib_maapi_onewire_pi_4_4 - \t{0}".format(msg))

    @classmethod
    def read_data_from_1w(self, rom_id, dev_id):
        if os.path.isfile('/sys/bus/w1/devices/{0}/w1_slave'.format(rom_id)):
            w1_file = open('/sys/bus/w1/devices/{0}/w1_slave'.format(rom_id),'r')
            self._debug(1,
                        "Open file /sys/bus/w1/devices/{0}/w1_slave"
                        .format(rom_id))
            w1_line = w1_file.readline()
            w1_crc = w1_line.rsplit(' ', 1)
            w1_crc = w1_crc[1].replace('\n', '')
            if w1_crc == 'YES':
                self._debug(2, "CRC - YES")
                w1_line = w1_file.readline()
                w1_temp = w1_line.rsplit('t=', 1)
                temp = float(float(w1_temp[1]) / float(1000))
                self._debug(
                    1, "Read_data_from_1w - Value is {0} for rom_id[1] {1}".
                    format(temp, dev_id))
                w1_file.close()
                self._debug(2, "Close file")
                maapidb.MaaPiDBConnection.insert_data(
                    dev_id, temp, ' ', True)
            else:
                w1_file.close()
                self._debug(2, "CRC False")
                maapidb.MaaPiDBConnection.insert_data(dev_id, 99999, ' ',
                                                      False)
        else:
            self._debug(
                1, "\tERROR reading values from rom_id[1]: {0}".format(dev_id))
            maapidb.MaaPiDBConnection.insert_data(dev_id, 99999, ' ', False)



    @classmethod
    def __init__(self, *args):
        for rom_id in args:
            condition, condition_min_max, force_value = Check().condition(
                rom_id[0])
            self._debug(
                1,
                "Condition is = {0}\t condition_min_max is = {1}, \t forced value is = {2}".
                format(condition, condition_min_max, force_value))
            if condition:
                if condition_min_max:
                    self.read_data_from_1w(rom_id[1], rom_id[0])
                    

                else:

                    maapidb.MaaPiDBConnection.insert_data(
                        rom_id[0], force_value, ' ', True)
                    self._debug(
                        1,
                        "Forcing value for sensor id = {0} \tforced vslur is = {1} ".
                        format(rom_id[0], force_value))
            else:
                self.read_data_from_1w(rom_id[1], rom_id[0])