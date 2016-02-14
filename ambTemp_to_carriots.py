#!flask/bin/python
# Filename: ambTemp_to_carriots.py
#
#--------------------------------------------------------
#   program will read the last 15 temperatures from app.db
#   average the readings and send them to carriots
#   program will execute every 15 minutes via apscheduler
#   8/4/14 -- Added the ambTemp_to_Sense to create a public
#   dashboard accessible from any browser.
#--------------------------------------------------------

import subprocess, re
import sys, time
import logging
import sqlite3 as lite
import carriots

import ambTemp_to_Sense

def send_temp():
    logging.debug("ambTemp_to_carriots.py program called.")

    #get the last 15 ambient_temp entries in the database.
    logging.debug("querying database for last 15 temp entries")
    
    con = lite.connect('/home/pi/tstat/app.db')
    cur = con.cursor()
    
    sql = "SELECT * from ambient_temps ORDER BY id DESC limit 15;" 
    cur.execute(sql)
    
    ambient_temps = cur.fetchall()
    
    total = 0
    humid_total = 0

    #process query, average temps
    for temps in ambient_temps:
        total = temps[2] + total                #column 2 is temperature from ambient_temps table in app.db
        humid_total = temps[3] + humid_total    #column 3 is humidity from ambient_temps table in app.db

    #calculate average
    avg_temp = total / 15
    avg_humidity = humid_total / 15

    #send this to carriots
    carriots_client = carriots.Client()

    logging.debug("attempting to write to carriots")
    senddata = { "temperature" : avg_temp,
                 "humidity"    : avg_humidity }

    carriots_response = carriots_client.send("LakePi", senddata)

    if carriots_response.code is 200:
        logging.debug("carriots has accepted the data, response code : %s", carriots_response.code)
        #get current time in python datetime format
        now = time.time()
        print str(now) + " : Avg temp = " + str(avg_temp) + " - avg humidity = " + str(avg_humidity)
        print str(now) + " : SUCCESS - data uploaded to carriots.com"
    else:
        logging.warning("Upload of data to Carriots.com failed")
        logging.debug("carriots response  ======== START")
        logging.debug(carriots_response.read())
        logging.debug("carriots response ======== END")
        logging.debug("carriots response INFO ======== START")
        logging.debug(carriots_response.info())
        logging.debug("carriots response ======== END")
        print "trouble sending data to carriots."
    carriots_response.close()

    #Need to add error trapping here.  No response from sense drops whole program.
    #Begin portion of program to send temperature to Sense
    #logging.debug("Calling ambTemp_to_Sense")
    #ambTemp_to_Sense.send_temp(avg_temp)
