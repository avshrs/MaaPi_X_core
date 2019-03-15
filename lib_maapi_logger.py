import logging
from datetime import datetime as dt


class Logger():
    def __init__(self):
        self.defaultDebugLevel = 1

    def log(self, level, msg):
        if self.defaultDebugLevel >= level:
            print("DEBUG | libLinuxCmd | {0} {1},\t| {2}".format(level, dt.now(), msg))