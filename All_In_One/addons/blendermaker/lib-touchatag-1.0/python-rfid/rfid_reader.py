#!/usr/bin/python


import os,sys
import subprocess as sub


print("Reading RFID...")

#p = sub.Popen('./rfidreader',stdout=sub.PIPE,stderr=sub.PIPE)
#output, errors = p.communicate()
#print output[len(output)-12:]
os.system("./rfidreader")

