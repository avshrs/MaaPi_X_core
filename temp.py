#!/usr/bin/python
import sys
from statistics import median, stdev, mean
from datetime import datetime as dt
from lim_maapi_i2c_bus import I2C_MaaPi



class class_get_values(object):
    debug = 1
    def __init__(self, address, sens, loops):
        self.addr = address
        self.loop = loops
        self.sensor = sens

        self.bus = I2C_MaaPi(1)


    def readFromI2C(self):

        data = self.bus.write_read_i2c_block_data32(int(self.addr,16),int(self.sensor),int(self.sensor),int(self.loop))

        print (f"min \tvalue: {min(data)}")
        print (f"mean \tvalue: {mean(data)}")
        print (f"max \tvalue: {max(data)}")
        print (f"median \tvalue: {median(data)}")
        print (f"stdev \tvalue: {stdev(data)}")

if __name__ == "__main__":
    class_get_values_ =  class_get_values(sys.argv[1], sys.argv[2], sys.argv[3])
    class_get_values_.readFromI2C()


