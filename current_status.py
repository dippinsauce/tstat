# Filename: current_status.py

#--------------------------------------------------------
# Defining a class for Thermostat status
# 
# get_temp = Defines a function to update the current temperature inside the house
# get_outside_temp = Defines a function to update the outside temperature as reported by 
#   wunderground for Coldwater, MI
#--------------------------------------------------------
import logging
import sqlite3 as lite

def get_temp():
    '''Gets the house temperature by querying app.db for the last 3 entires (one minute
    per reading)'''
    logging.debug("current_status.get_temp: called")
    
    logging.debug("current_status.get_temp: querying database for last 3 temp entries")
    
    con = lite.connect('/home/pi/tstat/app.db')
    cur = con.cursor()
    #get the last 3 ambient_temp entries in the database.
    sql = "SELECT temperature from ambient_temps ORDER BY id DESC limit 3;" 
    cur.execute(sql)
    
    temps = cur.fetchall()
    
    
    #average temps
    total = 0
    for temps in temps:
        total = temps[0] + total                #column 2 is temperature from ambient_temps table in app.db
    
    #calculate average
    return total / 3

from requests import get
from string import rstrip
import json, time

def get_outside_temp():
    '''Gets the outside temp from wunderground.com for coldwater, mi.  Updated
    every 15 minutes.  Current temp is last entry to outside temp table in 
    app.db'''
    logging.debug("current_status.get_outside_temp: called")
    logging.debug("current_status.get_outside_temp: check timestamp for last entry in db")
    
    con = lite.connect('/home/pi/tstat/app.db')
    cur = con.cursor()
    #get the timestamp from the last entry
    sql = "SELECT timestamp, temperature from outside_temps ORDER BY id DESC limit 1;"
    cur.execute(sql)
    
    QueryResult = cur.fetchall()
    Record = QueryResult[0]
    LastTime = Record[0]
    
    #check to see if last time was in the last 15 minutes (900 seconds)
    now = time.time()
    logging.debug("current_status.get_outside_temp: Last Time = %s", LastTime)
    logging.debug("current_status.get_outside_temp: now       = %s", now)
    logging.debug("current_status.get_outside_temp: now - 900 = %s", (now - 900))
    
    if LastTime > (now - 900):
        #we have updated in the last 15 minutes
        logging.debug("current_status.get_outside_temp: temp is fresh, returning last entry from db")
        con.close()
        return Record[1]
    else:
        #it's been longer than 15 mintues.  Update from wunderground.com
        # writing a function to get the outdoor temperature as reported by wunderground.com
        #   Using example found http://www.pythonforbeginners.com/python-on-the-web/scraping-wunderground/
        #   Also following example found http://www.wunderground.com/weather/api/d/docs?d=resources/code-samples&MR=1
        prefix =    'http://api.wunderground.com/api/'
        API_KEY =   '5fa3729fc702f2df'
        suffix =    '/geolookup/conditions/q/'
        extension = '.json'    
        location = 'MI/Coldwater'
    
        url = prefix + API_KEY + suffix + location + extension
        logging.debug("current_status.get_outside_temp: updating temp from wunderground.")
        logging.debug("current_status.get_outside_temp: url = %s", url)
        response = get(url)
        json_response = response.json()
        outside_temp = json_response['current_observation']['temp_f']
        tmp = json_response['current_observation']['relative_humidity']
        outside_humidity = float(rstrip(tmp,"%"))
        
        #need to write new temperature to database
        sql = "INSERT INTO outside_temps(timestamp, temperature, humidity) VALUES (" + str(now) + \
                    "," + str(outside_temp) + "," + str(outside_humidity) + ");"
        try:
            logging.debug("current_status.get_outside_temp: sql command = %s", sql)
            cur.execute(sql)    
            con.commit()
        except:
            logging.warning("current_status.get_outside_temp: Failed to write to database.")
        finally:
            logging.debug("current_status.get_outside_temp: I'm closing the db connection")
            con.close()
            
        return outside_temp
       