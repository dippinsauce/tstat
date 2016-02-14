#!flask/bin/python
# Filename : ambient_temp.py
# -*- coding: utf-8 -*-
#--------------------------------------------------------
#   program will read the temperature and humidity from dht22 hooked up
#   according to Adafruit instructions found at...
#       http://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/wiring
#   program will run once per minute via a tstat/apscheduler  and log readings to
#   the sqlite database being used for the thermostat application.
#--------------------------------------------------------

import subprocess, re
import sys, time
import logging
import sqlite3 as lite

def get_temp():
    '''Gets the ambient temperature via dht-22 sensor and write to the database'''
    logging.debug("ambient_temp.get_temp: has been called.")

    # Base Variables
    GPIO_Pin_Number     = "4"
    DHT_Number          = "2302"
    DHT_Program         = "/home/pi/Adafruit-Raspberry-Pi-Python-Code/Adafruit_DHT_Driver/Adafruit_DHT"
    SUDO                = "sudo"

    #call the adafruit program to read temp and humidity.
    while (True):
        command = SUDO + " " + DHT_Program + " " + DHT_Number + " " + GPIO_Pin_Number
        return_code = subprocess.check_output(command, shell=True)

        logging.debug("ambient_temp.get_temp: ==BEGIN== output from DHT Program")
        logging.debug(return_code)
        logging.debug("ambient_temp.get_temp: ===END===")

        #parse for temperature and humidity
        matches = re.search("Temp =\s+([0-9.]+)", return_code)
        if matches:
            temp = float(matches.group(1))
            #print("Data found")
            matches = re.search("Hum =\s+([0-9.]+)", return_code)
            humidity= float(matches.group(1))
            logging.debug("ambient_temp.get_temp: Temperature  = %s deg C, Humidity = %s percent", temp, humidity)
            break

        else:
            logging.debug("ambient_temp.get_temp: Couldn't find data in response")
            logging.debug("ambient_temp.get_temp: Waiting 3 seconds and trying again")
            time.sleep(3)

    #convert temperature to deg F from deg C
    temp = ((temp * 9)/5) + 32
    logging.debug("ambient_temp.get_temp: Temperature = %s deg F", temp)
    #get current time in python datetime format
    now = time.time()

    #write data to database
    logging.debug("ambient_temp.get_temp: Time: %s - Writing temperature and humidity to database", now)
    #print str(now) + " : Temp= " + str(temp) + " deg F, Humidity= " + str(humidity) + "%"
    sql = "INSERT INTO ambient_temps(timestamp, temperature, humidity) VALUES (" + str(now) + \
                    "," + str(temp) + "," + str(humidity) + ");"

    con = lite.connect('/home/pi/tstat/app.db')
    cur = con.cursor()

    try:
        cur.execute(sql)    
        con.commit()
    except:
        logging.warning("ambient_temp.get_temp: Failed to write to database.")
    finally:
        con.close()