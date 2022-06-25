#!/usr/bin/env python3
#========================================================================
# BMP.py
# Autor: Lukas Jordan
# Datum: 17.06.2022
# Description: Includes the handler which reads in the 
# 
# !!!!!!!!!!!!!!I2C must be activated in the Interface Options (third Point) in raspi-config !!!!!!!!!!!      
#========================================================================
# Imports
from Adafruit_BMP085 import BMP085
import datetime
import os
from time import sleep
from multiprocessing import Process

#=======================================================================
# Sensor Settings


#======================================================================

class BMP_handler(Process):
    
    def __init__(self,interval,log_path):
        super(BMP_handler,self).__init__()
        self.interval = interval
        self.log_path = log_path
        self.bmp = BMP085(0x77)

    def run(self):
        print("BMP Reading started...")
        while(1):
            sleep(self.interval)
            temperature = self.bmp.readTemperature()
            pressure = self.bmp.readPressure()

            if pressure is not None and temperature is not None:
                today = datetime.datetime.now()
                # check for file existens
                if os.path.exists(self.log_path):

                    if os.stat(self.log_path).st_size == 0:
                        f = open(self.log_path, "a+")
                        f.write('Date,Time,Temperature,Pressure\n')
                    else:
                        f = open(self.log_path, "a+")
                else:
                    f = open(self.log_path, "a+")
                    f.write('Date,Time,Temperature,Pressure\n')
                
                f.write(str(today.strftime("%Y/%m/%d")) +','+ str(today.strftime("%H:%M:%S")) + ',{0:0.1f},{1:0.1f}'.format(temperature, pressure)+'\n')
                f.close()