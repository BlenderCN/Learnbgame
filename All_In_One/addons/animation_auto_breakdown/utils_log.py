#!BPY
# -*- coding: UTF-8 -*-
# Utilities of Logging
#
# 2017.07.17 Natukikazemizo
import datetime

class Util_Log():
    def __init__(self, py_name):
        self.py_name = py_name

    def log(self, str):
        print(datetime.datetime.today().\
            strftime("%Y/%m/%d %H:%M:%S ") + self.py_name + " " + str)

    def detailtime_log(self, str):
        print(datetime.datetime.today().\
            strftime("%Y/%m/%d %H:%M:%S.%f ") + self.py_name + " " + str)

    def start(self):
        self.info("### START ###")

    def end(self):
        self.info("### END   ###")

    def info(self, str):
        self.log("INFO:" + str)

    def warn(self, str):
        self.log("WARN:" + str)

    def err(self, str):
        self.log("ERR :" + str)
