#!/home/pi/tstat/flask/bin/python

import logging
#initialize logging capability
loglevel = "DEBUG"
logFileName = ("/home/pi/tstat/app.log")
logging.basicConfig(filename=logFileName, level=loglevel,
                    format='%(asctime)s %(levelname)s %(message)s')
logging.debug("===========================logger started")

def supervisor():
    #function to run automatic mode of thermostat and keep you from breaking things
    logging.debug("SUPERVISOR: function called.")
    #get outside temp in coldwater, MI
    outside_temp = current_status.get_outside_temp()
    inside_temp = current_status.get_temp()
    logging.debug("SUPERVISOR: Temperature: inside - %s", inside_temp)
    logging.debug("SUPERVISOR: Setpoint %s", status['setpoint'])
    #What mode are we in?
    if status['mode'] is 'bypass':
        #Tstat is in bypass, make sure everything is off.
        logging.debug("SUPERVISOR: Mode: bypass, verifying that all outputs are off")
        hheat.off()
        lheat.off()
        cool.off()
        fan.off()
    if status['mode'] is 'auto':
        #Tstat, compare setpoint temp, actual temp, and outside temp.
        #Are we calling for heat or cooling?
        if status['setpoint'] > outside_temp:
            #Heat Mode
            if inside_temp > (status['setpoint'] + 1):
                hheat.off()
                lheat.off()
                logging.debug("SUPERVISOR: Mode: Auto - Heat, turning OFF heat, temp %s, setpoint %s", inside_temp, status['setpoint'] )
            if inside_temp < (status['setpoint'] - 1):
                hheat.on()
                logging.debug("SUPERVISOR: Mode: Auto - Heat, turning ON heat, temp %s, setpoint %s", inside_temp, status['setpoint'] )
        else:
            #cool mode
            if inside_temp < (status['setpoint'] - 1):
                cool.off()
                fan.off()
                logging.debug("SUPERVISOR: Mode: Auto - Cool, turning OFF cool, temp %s, setpoint %s", inside_temp, status['setpoint'] )
            if inside_temp > (status['setpoint'] + 1):
                cool.on()
                fan.on()
                logging.debug("SUPERVISOR: Mode: Auto - Cool, turning ON cool, temp %s, setpoint %s", inside_temp, status['setpoint'] )
    
    if status['mode'] is 'manual':
        #don't do much here.  check for bad things below.
        pass
    #========================================================================================
    #Look for bad things and correct them.
    #========================================================================================
    #is heat and cool on at the same time?
    if (hheat.status() or lheat.status()) and cool.status():
        logging.warning("SUPERVISOR: A heat output and cooling output are on simultaneously.  Turning off!")
        status['mode'] = 'bypass'
        hheat.off()
        lheat.off()
        cool.off()
        fan.off()
    
    #make sure it isn't too cold to be running air conditioning
    if cool.status() and outside_temp < 60:
        logging.warning("SUPERVISOR: It's too cold for air conditioning.  Turning off output")
        cool.off()
        status['mode'] = 'bypass'
    #make sure it isn't too hot for heat
    if (hheat.status() or lheat.status()) and outside_temp > 65:
        logging.warning("SUPERVISOR: It's too hot for heat.  Turning off output")
        hheat.off()
        lheat.off()
        status['mode'] = 'bypass'

from flask import Flask, render_template, flash, redirect, url_for
from flask_wtf import Form
from forms import AutoForm, ManualForm

def create_app(configfile=None):
    app = Flask(__name__)
    
    # set the secret key.  keep this really secret:
    app.secret_key = 'A0Zr98j/aoshuidgvp[08baHH!jmN]LWX/,?RT'
    
    @app.before_request
    def before_request():
        status['temp'] = "{0:.1f}".format(current_status.get_temp())
        status['outside_temp'] = "{0:.1f}".format(current_status.get_outside_temp())
        status['hheat'] = hheat.status()
        status['lheat'] = lheat.status()
        status['cool'] = cool.status()
        status['fan'] = fan.status()
    
    @app.route("/")
    @app.route("/index")
    def index():
        return render_template("index.html", **status)
    
    @app.route("/tstat")
    def tstat():
        return render_template("tstat.html", **status)
        
    @app.route("/tstat/auto", methods = ['GET', 'POST'])
    def auto():
        form = AutoForm()
        
        if form.validate_on_submit():
            status['setpoint'] = form.setpoint.data
            status['mode'] = 'auto'
            supervisor()
            return redirect(url_for('tstat'))
        else:
            flash("Desired Temperature must be between 45 and 85")
            status['mode'] = 'bypass' #set bypass so supervisor will not act until corrent temp entered
        return render_template("auto.html", form = form, **status)  
        #two astericks splat operator
        
    @app.route("/tstat/manual", methods = ['GET', 'POST'])
    def manual():
        return render_template("manual.html", **status)
    
    @app.route("/tstat/manualop/<action>/<request_state>")
    def manual_op(action = None, request_state = None):
        if action == 'hheat':
            if request_state == 'on':
                hheat.on()
                flash("High Heat has been turned on")
            else:
                hheat.off()
                flash("High Heat has been turned off")
        elif action == 'lheat':
            if request_state == 'on':
                lheat.on()
                flash("Low Heat has been turned on")
            else:
                lheat.off()
                flash("Low Heat has been turned off")
        elif action == 'cool':
            if request_state == 'on':
                cool.on()
                flash("Cooling has been turned on")
            else:
                cool.off()
                flash("Cooling has been turned off")
        elif action == 'fan':
            if request_state == 'on':
                fan.on()
                flash("Fan has been turned on")
            else:
                fan.off()
                flash("Fan has been turned off")
        else:
            flash("Command not accepted, no action being taken")
        status['mode'] = 'manual'
        return redirect(url_for('manual'))
        
    @app.route("/tstat/bypass")
    def bypass():
        status['mode'] = 'bypass'
        supervisor()
        return redirect(url_for('tstat'))
    
    return app

    
if __name__ == "__main__":

    from apscheduler.scheduler import Scheduler
    import ambient_temp, ambTemp_to_carriots

    #program just started, go ahead and send some data to carriots.
    logging.debug("Program Started: sending data to carriots to reset device status")
    ambTemp_to_carriots.send_temp()

    #start the apscheduler
    scheduler = Scheduler()
    logging.debug("starting the scheduler")
    scheduler.start()

    #get temp and humidity and write to database every minute
    logging.debug("adding ambient_temp.get_temp to the scheduler")
    scheduler.add_cron_job(ambient_temp.get_temp, minute="*/1")

    #send the average temp and humidity from the last 15 minutes
    logging.debug("adding ambTemp_to_carriots to the scheduler")
    scheduler.add_cron_job(ambTemp_to_carriots.send_temp, minute="*/15")

    #start the thermostat supervisor
    logging.debug("adding supervisor to the scheduler")
    scheduler.add_interval_job(supervisor, minutes = 1)

    from ConfigParser import SafeConfigParser
    import sys
    #Get the GPIO pin addresses and names for initialization.
    logging.debug("opening and reading configuration file")
    parser = SafeConfigParser()
    parser.read('/home/pi/tstat/config.ini')

    #create the class for each gpio pin
    import gpio_pin
    logging.debug("creating gpio_pin classes")
    for name, value in parser.items('GPIO'):
        if name == "heatw1":
            lheat = gpio_pin.gpio_pin("heatw1",value)
        elif name == "heatw2":
            hheat = gpio_pin.gpio_pin("heatw2",value)
        elif name == "cool":
            cool = gpio_pin.gpio_pin("cool",value)
        elif name == "fan":
            fan = gpio_pin.gpio_pin("fan",value)
        else:
            print "there is an error in the config.ini file"
            print "exiting program"
            logging.error("one the gpio config.ini entries is incorrect, exiting program")
            sys.exit(1)

    #create the status dict for passing to the webpage
    import current_status
    tmp_temp = "{0:.1f}".format(current_status.get_temp())
    out_temp = "{0:.1f}".format(current_status.get_outside_temp())
    status = {
                'mode' : 'bypass',      #three modes are available (bypass, auto, manual)
                'control' : 'heat',     #three control are available (heat, cool, fan)
                'setpoint' : None,        #setpoint for thermostat calculation
                'temp' : tmp_temp,      #current temperature stored here
                'outside_temp' : out_temp,
                'hheat' : hheat.status(),
                'lheat' : lheat.status(),
                'cool' : cool.status(),
                'fan' : fan.status()
        }
    
    create_app().run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
