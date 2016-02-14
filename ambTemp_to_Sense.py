#!flask/bin/python
# Filename: ambTemp_to_Sense.py
#
#--------------------------------------------------------
#   program will send the number passed to it to open.sen.se
#   It will update the feed created for LakePi, Inside House Temperature, Feed #57282
#--------------------------------------------------------

import logging
import simplejson
import requests

class Sense:
    def __init__(self, senseKey):
        self.url        = 'http://api.sen.se'
        self.headers    = {'Content-Type':'application/json', 'sense_key':senseKey}

    def post(self,feedId, value):
        event = {
            'feed_id'   : feedId,
            'value'     : value
        }
        logging.info("Now posting to Sen.se : %s" % event)
        r = requests.post(
            self.url+'/events/',
            data=simplejson.dumps(event),
            headers=self.headers
        )
        if r.status_code != 200:
            logging.debug('Could not post event. Api responded with a %s | %s' % (r.status, r.content))
        else:
            logging.debug('Event posted to Sen.se')

def send_temp(avg_temp):
    logging.debug("Posting to Sense...")
    sense = Sense('fVc37tFjUWT8oSMSq4PCFg')
    #feed 57282 -- LakePi -> Inside House Temperature
    sense.post(57282, avg_temp)