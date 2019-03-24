#!/usr/bin/python
import sys
from statistics import median, stdev, mean
from datetime import datetime as dt
from lim_maapi_i2c_bus import I2C_MaaPi



class class_get_values(object):
    debug = 1
    def __init__(self, address, sens, loops, rel):
        self.addr = address
        self.loop = loops
        self.sensor = sens
        self.rel = int(rel)
        self.bus = I2C_MaaPi(1)


    def readFromI2C(self):
        data = self.bus.write_read_i2c_block_data32(int(self.addr,16),int(self.sensor),int(self.sensor),2)
        data = self.bus.write_read_i2c_block_data32(int(self.addr,16),int(self.sensor),int(self.sensor),int(self.loop))
        print (data)
        out = []
        for d in data:
            tym = d - self.rel
            out.append(tym)
        print (f"min \tvalue: {min(out)}")
        print (f"mean \tvalue: {mean(out)}")
        print (f"max \tvalue: {max(out)}")
        print (f"median \tvalue: {median(out)}")
        print (f"stdev \tvalue: {stdev(out)}")

        out2=[]
        for o in out:
            tym = abs(o)
            out2.append(tym)

        print (f"min \tvalue: {min(out2)}")
        print (f"mean \tvalue: {mean(out2)}")
        print (f"max \tvalue: {max(out2)}")
        print (f"median \tvalue: {median(out2)}")
        print (f"stdev \tvalue: {stdev(out2)}")



if __name__ == "__main__":
    class_get_values_ =  class_get_values(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    class_get_values_.readFromI2C()


