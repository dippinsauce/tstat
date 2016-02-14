#!/home/pi/tstat/flask/bin/python

# writing a function to get the outdoor temperature as reported by wunderground.com
#   Using example found http://www.pythonforbeginners.com/python-on-the-web/scraping-wunderground/
#   Also following example found http://www.wunderground.com/weather/api/d/docs?d=resources/code-samples&MR=1

import logging
from requests import get
import json

#initialize logging capability
logging.debug("wunderground.py has been called")

prefix =    'http://api.wunderground.com/api/'
API_KEY =   '5fa3729fc702f2df'
suffix =    '/geolookup/conditions/q/'
extension = '.json'    

def get_outside_temp_coldwater():
    
    location = 'MI/Coldwater'
    
    url = prefix + API_KEY + suffix + location + extension
    logging.debug("wunderground.get_outside_temp_coldwater has been called")
    logging.debug("url = %s", url)
    
    response = get(url)
    json_response = response.json()
    
    return json_response['current_observation']['temp_f']