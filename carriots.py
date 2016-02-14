#!/home/pi/tstat/flask/bin/python

#--------------------------------------------------------
#A library for communicating with carriots...
#
# create the instance by passing...
#   device: string which is the name of the device on Carriots (case sensitive)
#       don not include the '@dippinsuace' at the end.
#   data: data is sent as a dict which includes
#        the stream name as created in carriots - and the data
# most of the code was adapted from the example found...
# https://www.carriots.com/tutorials/raspberrypi_carriots/alert_system
# it's been modified to be a more general function.
#--------------------------------------------------------

import urllib2
import datetime, time
import json

API_KEY = "335bfc7b68243ee3663e7370fdbc370e883c2f398630aeff0525648fadd8e12b"
USERNAME = "@dippinsauce"

#Setup class for communicating to Carriots.com
class Client(object):
  api_url = "http://api.carriots.com/streams"  
 
  def __init__(self, client_type = 'json'):
    self.client_type = client_type
    self.api_key = API_KEY
    self.content_type = "application/vnd.carriots.api.v2+%s" % (self.client_type)
    self.headers = {'User-Agent': 'Raspberry-Carriots',
                     'Content-Type': self.content_type,
                     'Accept': self.content_type,
                     'Carriots.apikey': self.api_key}

  def send(self, device, data):
    timestamp = int (time.mktime(datetime.datetime.utcnow().timetuple()))
    self.data = { "protocol" : "v2",
                    "device": str(device) + USERNAME,
                    "at": timestamp,
                    "data": data}
    self.data = json.dumps(self.data)
    request = urllib2.Request(Client.api_url, self.data, self.headers)
    self.response = urllib2.urlopen(request)
    return self.response