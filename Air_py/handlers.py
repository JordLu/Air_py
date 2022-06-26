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
import sys
sys.path.insert(0, './Driver')

from Adafruit_BMP085 import BMP085
import Adafruit_DHT
import lcddriver
import datetime
import os
from time import sleep, time
from multiprocessing import Process, Queue

#=======================================================================
# Sensor Settings
# DHT
DHT_SENSOR = Adafruit_DHT.AM2302
DHT_PIN = 21

# BMP

# Display Settings
LCD_REFRESH = 5 # Time in seconds before LCD Display refreshes
#======================================================================

class BMP_handler(Process):
    
    def __init__(self,interval_log,interval_refresh,log_path, queue):
        super(BMP_handler,self).__init__()
        self.log_path = log_path
        self.bmp = BMP085(0x77)

        if interval_log >= interval_refresh:
            self.interval_high = interval_log
            self.interval_low = interval_refresh
        else:
            self.interval_high = interval_refresh
            self.interval_low = interval_log
        
        self.q = queue

    def run(self):
        print("BMP Reading started...")
        start_time = time()
        while(1):
            sleep(self.interval_low)

            temperature = self.bmp.readTemperature()
            pressure = self.bmp.readPressure()

            print(temperature, pressure) # Testzeile

            if pressure is not None and temperature is not None:
                self.q.put(["Temperature",temperature])
                self.q.put(["Pressure",pressure])

                if (time()-start_time) >= self.interval_high:
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


class DHT_handler(Process):
    
    def __init__(self,interval_log,interval_refresh,log_path,queue):
        super(DHT_handler,self).__init__()
        self.log_path = log_path

        if interval_log >= interval_refresh:
            self.interval_high = interval_log
            self.interval_low = interval_refresh
        else:
            self.interval_high = interval_refresh
            self.interval_low = interval_log
        
        self.q = queue

    def run(self):
        print("DHT Reading started...")
        start_time = time()
        while(1):
            sleep(self.interval_low)
            humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

            if humidity is not None and temperature is not None:
                
                self.q.put(["Temperature",temperature])
                self.q.put(["Humidity",humidity])

                if (time()-start_time) >= self.interval_high:
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


class lcd_handler(Process):
    
    def __init__(self,queue):
        super(lcd_handler,self).__init__()
        self.q = queue
        
    def run(self):
        try:
            lcd = lcddriver.lcd()
        except OSError:
            print("Error connecting to LCD: Check I2C Connection")
            return -1

        try:
            lcd.lcd_clear()
            lcd.lcd_display_string(" Air Pi", 1)
            lcd.lcd_display_string("", 2)
            lcd.lcd_display_string(" Starting ...", 3)
            lcd.lcd_display_string(" ", 4)
            sleep(5)

            temperature = 0
            humidity = 0 
            pressure = 0

            while(1):
                sleep(LCD_REFRESH)
                if not self.q.empty():
                    value = self.q.get()

                    if value[0] == "Temperature":
                        temperature = value[1]
                    elif value[0] == "Humidity":
                        humidity = value[1]
                    elif value[0] == "Pressure":
                        pressure = value[1]
                
                lcd.lcd_clear()
                lcd.lcd_display_string(str(today.strftime("%d.%m.%Y")) + " " + str(today.strftime("%H:%M")), 1)
                lcd.lcd_display_string("Temperature: " + '{0:0.1f}'.format(temperature), 2)
                lcd.lcd_display_string("Humidity: " + '{0:0.1f}'.format(humidity), 3)
                lcd.lcd_display_string("Pressure: " + '{0:0.1f}'.format(pressure), 4)

        except KeyboardInterrupt:
	        lcd.lcd_clear()