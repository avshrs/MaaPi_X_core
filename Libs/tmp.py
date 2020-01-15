import integra 
from constants import INPUTNAMES, OUTPUTNAMES
import time
from datetime import datetime as dt

class Int():
    def __init__(self):
        self.integ = integra.Integra(user_code=1234, host='192.168.1.240', port=25197)
        self.inputs = []
        self.outputs = []
        self.in_table = {}
        self.out_table = {}
        self.interval = 10
    def get_inputs(self):
        try:
            self.inputs = self.integ.get_violated_zones()
        except Exception as e:
            print(dt.now(), e)
        for i in self.inputs:
            if i == 15 or i == 16:
                break
            if i not in self.in_table:
                print(dt.now(), "in", i, "\t", INPUTNAMES[i])
                self.in_table[i] = dt.now()
            elif (dt.now() - self.in_table[i]).seconds >= self.interval:
                self.in_table[i] = dt.now()
                print(dt.now(), "in", i, "\t", INPUTNAMES[i])
        self.inputs = []

    def get_outputs(self):
        try:
            self.outputs = self.integ.get_active_outputs()
        except Exception as e:
            print(dt.now(), e)

        for i in self.outputs:

            if i not in self.out_table:
                print(dt.now(), "out", i, "\t", OUTPUTNAMES[i])
                self.out_table[i] = dt.now()

            elif (dt.now() - self.out_table[i]).seconds >= self.interval:
                self.out_table[i] = dt.now()
                print(dt.now(), "out", i, "\t", OUTPUTNAMES[i])
        self.outputs = []
    def loop(self):
        while True:
            self.get_inputs()
            # self.get_outputs()
            time.sleep(0.1)
            
if __name__ == "__main__":
    i = Int()
    i.loop()        