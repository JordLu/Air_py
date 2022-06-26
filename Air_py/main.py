#!/usr/bin/env python3
#========================================================================
# main.py
# Autor: Lukas Jordan
# Datum: 17.06.2022
# Description: 
#
#========================================================================
# Imports
import Adafruit_DHT
import handlers
import datetime
import os
from time import sleep
from multiprocessing import Queue

#======================================================================
# Log Settings 
# Names of sensor loggings
DHT_LOG_NAME = "DHT_log.csv"
BMP_LOG_NAME = "BMP_log.csv"
# Name of Directory for logs
LOG_DIR = 'logs'

# interval for loging and refreshing the values on LCD in seconds
INTERVAL_LOG = 60
INTERVAL_LCD = 1

#=======================================================================
def INIT_dir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)
    pass


if __name__ == "__main__":
    INIT_dir(LOG_DIR) # create log dir

    q = Queue()

    # Setup Handlers
    DHT_hnd = handlers.DHT_handler(INTERVAL_LOG,INTERVAL_LCD,os.path.join(os.path.dirname(__file__),LOG_DIR,DHT_LOG_NAME),q)
    BMP_hnd = handlers.BMP_handler(INTERVAL_LOG,INTERVAL_LCD,os.path.join(os.path.dirname(__file__),LOG_DIR,BMP_LOG_NAME),q)
    LCD_hnd = handlers.lcd_handler(q)

    # Start Handlers
    DHT_hnd.start()
    BMP_hnd.start()
    LCD_hnd.start()

    # Terminted Handlers after 60 Seconds 
    sleep(2)
    print("Now Exiting!!")

    DHT_hnd.terminate()
    BMP_hnd.terminate()
    LCD_hnd.terminate()


