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
import BMP
import datetime
import os
import DHT

# Settings 
# Sensor
DHT_LOG_NAME = "DHT_log.csv"
BMP_LOG_NAME = "BMP_log.csv"
# Log 
LOG_DIR = 'logs'

#=======================================================================
def INIT_dir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)
    pass


if __name__ == "__main__":
    INIT_dir(LOG_DIR) # create log dir

    # Setup Handlers
    DHT_hnd = DHT.DHT_handler(10,os.path.join(os.path.dirname(__file__),LOG_DIR,DHT_LOG_NAME))
    BMP_hnd = BMP.BMP_handler(10,os.path.join(os.path.dirname(__file__),LOG_DIR,BMP_LOG_NAME))
    
    # Start Handlers
    DHT_hnd.start()
    BMP_hnd.start()
    
    # Terminted Handlers after 60 Seconds 
    Wait(60)
    print("Now Exiting!!")
    DHT_hnd.terminated()
    BMP_hnd.terminated()


