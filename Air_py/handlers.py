#!/usr/bin/env python3
#========================================================================
# Handlers.py
# Version: 0.7
# Autor: Lukas Jordan
# Datum: 17.06.2022
# Description: Includes the Handler for the LCD Dislplay, BMP and DHT Sensor
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
# General
TIMES_BEFORE_FAULT = 10 # Times the sensor hasnt returned any Value, before it shows an Error on Display 

# IMPORTANT !!! Make sure LOG_INTERVAL > DATA_SEND_TO_LCD_INTERVAL
INTERVAL_LOG = 60 # min. Interval in seconds between logging a Value, in some cases it can be longer, i.e. no reading from sensor
INTERVAL_DATA_SEND_TO_LCD = 10 # seconds before new values being send to sensor

# DHT
DHT_SENSOR = Adafruit_DHT.AM2302    # Type of Sensor
DHT_PIN = 18                        # Pin of Sensor

# BMP
BMP_ADDRESS = 0x77  # I2C Address

# Display Settings
LCD_REFRESH = 5 # Time in seconds before LCD Display refreshes
#======================================================================

# =====================================================================
# BMP_Handler Class
# =====================================================================
# Handler for BMP Sensor (Pressure and Temperature), logging and sending data to LCD
class BMP_handler(Process):
    
    # Constructor
    def __init__(self, log_path, queue, interval_log = INTERVAL_LOG,interval_refresh = INTERVAL_DATA_SEND_TO_LCD):
        super(BMP_handler,self).__init__()  # Constructor for Process class
        self.log_path = log_path
        self.bmp = BMP085(BMP_ADDRESS)

        # Check for faulty input and make sure the log intervall is bigger than the refresh rate
        if interval_log >= interval_refresh:
            self.interval_high = interval_log
            self.interval_low = interval_refresh
        else:
            self.interval_high = interval_refresh
            self.interval_low = interval_log
        
        self.q = queue  # Queue for the Data send to LCD

    # Task
    def run(self):
        print("BMP Reading started...")
        start_time = time() # Time used for logging timer
        no_value = 0    # Value of no readings
        
        while(1):
            sleep(self.interval_low)

            # Reading of Temprature and pressure
            temperature = self.bmp.readTemperature() 
            pressure = self.bmp.readPressure()

            if pressure is not None and temperature is not None:
                # Send Data to LCD
                #self.q.put(["Temperature",temperature])    # Not Sending Temprature Reading to LCD, because DHT Reading is used 
                self.q.put(["Pressure",pressure])

                no_value = 0    # Set times no Value could be read to 0

                # Check if it is time to log
                if (time()-start_time) >= self.interval_high:
                    today = datetime.datetime.now() # Save current date and time
                    # check for file existens
                    if os.path.exists(self.log_path):
                        # check if file exists and no header is writen
                        if os.stat(self.log_path).st_size == 0:
                            f = open(self.log_path, "a+")
                            f.write('Date,Time,Temperature,Pressure\n')
                        else:
                            f = open(self.log_path, "a+")
                    # Create the File and write Header 
                    else:
                        f = open(self.log_path, "a+")
                        f.write('Date,Time,Temperature,Pressure\n')
                    
                    # Log Data
                    f.write(str(today.strftime("%Y/%m/%d")) +','+ str(today.strftime("%H:%M:%S")) + ',{0:0.1f},{1:0.1f}'.format(temperature, pressure/100.0)+'\n')
                    f.close()
                    
                    start_time = time() # Reset timer for logging
            # Else for the case no Readings could be made
            else:
                no_value += 1   # increase counter 
                print("Error: No Reading from BMP Sensor!! Check Connection!! ")
                if no_value == TIMES_BEFORE_FAULT: # if critical value is reached send none to LCD handler
                    #self.q.put(["Temperature",None])
                    self.q.put(["Pressure",None])

# =====================================================================
# DHT_Handler Class
# =====================================================================
# Handler for DHT Sensor (Humidity and Temperature), logging and sending data to LCD
class DHT_handler(Process):
    # Constructor
    def __init__(self, log_path, queue, interval_log = INTERVAL_LOG,interval_refresh = INTERVAL_DATA_SEND_TO_LCD):
        super(DHT_handler,self).__init__()
        self.log_path = log_path

        # Check for faulty input and make sure the log intervall is bigger than the refresh rate
        if interval_log >= interval_refresh:
            self.interval_high = interval_log
            self.interval_low = interval_refresh
        else:
            self.interval_high = interval_refresh
            self.interval_low = interval_log
        
        self.q = queue  # Queue for the Data send to LCD

    # Task
    def run(self):
        print("DHT Reading started...")
        start_time = time() # Time used for logging timer
        no_value = 0    # Value of no readings

        while(1):
            sleep(self.interval_low)

            # Try to Read temperatur and humidity
            humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
            # check for Success
            if humidity is not None and temperature is not None:
                # Send data to LCD
                self.q.put(["Temperature",temperature])
                self.q.put(["Humidity",humidity])

                # Check if it is time to log
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
                    start_time = time() # Reset Loging timer
            # Case of No Reading
            else:
                no_value += 1
                print("Error: No Reading from DHT Senson!! Check Connection!!")
                # Show nA on LCD
                if no_value == TIMES_BEFORE_FAULT:
                    self.q.put(["Temperature",None])
                    self.q.put(["Humidity",None])

# =====================================================================
# lcd_handler Class
# =====================================================================
# Handler for the LCD, handles output on LCD and the data shown
class lcd_handler(Process):
    # Constructor
    def __init__(self,queue):
        super(lcd_handler,self).__init__()
        self.q = queue
        self.lcd = None

    # Task
    def run(self):
        # Try setting the LCD Driver
        try:
            self.lcd = lcddriver.lcd()
        except OSError:
            print("Error connecting to LCD: Check I2C Connection")
            return -1
        
        # Catch KeyboardException
        try:
            # Print Welcome 
            self.lcd.lcd_clear()
            self.lcd.lcd_display_string("Welcome", 1, 6)
            self.lcd.lcd_display_string("Air Pi", 2, 7)
            self.lcd.lcd_display_string(" ", 3,)
            self.lcd.lcd_display_string("Starting ...", 4, 5)
            sleep(10)

            # Set values to 0 to start
            temperature = 0
            humidity = 0
            pressure = 0

            while(1):
                today = datetime.datetime.now() # save current date and time for output
                while not self.q.empty():  # check for new sensor readings
                    value = self.q.get()

                    # Save to correct variable
                    if value[0] == "Temperature":
                        temperature = value[1]
                        self.clear_line(2)
                        if temperature is not None:
                            self.lcd.lcd_display_string("Temperature: " + '{0:0.1f}'.format(temperature) + " °C", 2)
                        else: 
                            self.lcd.lcd_display_string("Temperature: " + "N/A", 2)
                    elif value[0] == "Humidity":
                        humidity = value[1]
                        self.clear_line(3)
                        if humidity is not None:
                            self.lcd.lcd_display_string("Humidity: " + '{0:0.1f}'.format(humidity) + ' %', 3)
                        else:
                            self.lcd.lcd_display_string("Humidity: " + "N/A", 3)
                    elif value[0] == "Pressure":
                        pressure = value[1]
                        if pressure is not None:
                            self.lcd.lcd_display_string("Pressure: " + '{0:0.1f}'.format(pressure / 100.0) + ' hPa', 4)
                        else:
                            self.lcd.lcd_display_string("Pressure: " + "N/A", 4)
                
                # Clear LCD and print to Display
                #self.lcd.lcd_clear()
                self.clear_line(1)
                self.lcd.lcd_display_string(str(today.strftime("%d.%m.%Y")) + " " + str(today.strftime("%H:%M")), 1)
                #if temperature is not None:
                #    self.lcd.lcd_display_string("Temperature: " + '{0:0.1f}'.format(temperature) + " °C", 2)
                #else: 
                #    self.lcd.lcd_display_string("Temperature: " + "N/A", 2)
                #if humidity is not None:
                #    self.lcd.lcd_display_string("Humidity: " + '{0:0.1f}'.format(humidity) + ' %', 3)
                #else:
                #    self.lcd.lcd_display_string("Humidity: " + "N/A", 3)
                #if pressure is not None:
                #    self.lcd.lcd_display_string("Pressure: " + '{0:0.1f}'.format(pressure / 100.0) + ' hPa', 4)
                #else:
                #    self.lcd.lcd_display_string("Pressure: " + "N/A", 4)

                sleep(LCD_REFRESH)

        except KeyboardInterrupt:
	        lcd.lcd_clear()

    # Function to clear a line of the Display
    def  clear_line(self, line):
        self.lcd.lcd_display_string("                    ", line)    