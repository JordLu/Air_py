#!/usr/bin/env python3
#========================================================================
# DHT.py
# Autor: Lukas Jordan
# Datum: 17.06.2022
# Description: Includes the handler which reads in the 
#
#========================================================================
# Imports
import Adafruit_DHT
import datetime
import os
from time import sleep, time
from multiprocessing import Process, Queue
from types import c_value

#=======================================================================
# Sensor Settings
DHT_SENSOR = Adafruit_DHT.AM2302
DHT_PIN = 21

#======================================================================

class DHT_handler(Process):
    
    def __init__(self,interval_log,interval_refresh,log_path,q):
        super(DHT_handler,self).__init__()
        self.log_path = log_path

        if interval_log >= interval_lcd:
            self.interval_high = interval_log
            self.interval_low = interval_refresh
        else:
            self.interval_high = interval_refresh
            self.interval_low = interval_log
        
        self.q = queue

    def run(self):
        print("DHT Reading started...")
        start_time = time.time()
        while(1):
            sleep(self.interval)
            humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

            if humidity is not None and temperature is not None:
                self.q.put(c_value("Temperature",temperature))
                self.q.put(c_value("Pressure",pressure))

                if (time.time()-start.time) >= self.interval_high:
                    today = datetime.datetime.now()
                    # check for file existens
                    if os.path.exists(self.log_path):

                        if os.stat(self.log_path).st_size == 0:
                            f = open(self.log_path, "a+")
                            f.write('Date,Time,Temperature,Humidity\n')
                        else:
                            f = open(self.log_path, "a+")
                    else:
                        f = open(self.log_path, "a+")
                        f.write('Date,Time,Temperature,Humidity\n')
                    
                    f.write(str(today.strftime("%Y/%m/%d")) +','+ str(today.strftime("%H:%M:%S")) + ',{0:0.1f},{1:0.1f}'.format(temperature, humidity)+'\n')
                    f.close()
