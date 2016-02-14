#--------------------------------------------------------
# Defining a class for each gpio pin
#
# Creates a class for each gpio pin to track status, name
#--------------------------------------------------------

import subprocess, sys
import logging

#class added so we can iterate through all instances of gpio_pin
#example taken from http://stackoverflow.com/questions/739882/iterating-over-object-instances-of-a-given-class-in-python
class IterRegistry(type):
    def __iter__(cls):
        return iter(cls._registry)

class gpio_pin:
    #added so we can iterate through all instances
    __metaclass__ = IterRegistry
    _registry = []
    
    def __init__(self, name, pin):
        #added so we can iterate through all instances
        self._registry.append(self)
        
        self.name = name
        self.pin = pin
        #initialize the pin mode as write
        command = "sudo /home/pi/wiringPi/gpio/gpio mode " + str(pin) + " out"
        try:
            return_code = subprocess.check_output(command, shell=True)
        except:
            logging.error("gpio_pin.__init__: There is a problem initializing to the GPIO pins")
            print "Can't initialize GPIO pin"
            #if there is a problem writing to the GPIO pins, we have no business continuing
            sys.exit(1)
        
        #initialize the pin as off
        command = "sudo /home/pi/wiringPi/gpio/gpio write " + str(pin) + " 0"
        try:
            return_code = subprocess.check_output(command, shell=True)
        except:
            logging.error("gpio_pin.__init__: There is a problem writing to the GPIO pins")
            #print "Can't write to GPIO pins"
            #if there is a problem writing to the GPIO pins, we have no business continuing
            sys.exit(1)
    
    def status(self):
        command = "sudo /home/pi/wiringPi/gpio/gpio read " + str(self.pin)
        logging.debug("gpio_pin.status: checking status of pin %s, pin # %s", self.name, self.pin)
        return_code = subprocess.check_output(command, shell=True)
        #this isn't working!
        if return_code.rstrip() == "0":
            return False
        else:
            return True
    
    def on(self):
        command = "sudo /home/pi/wiringPi/gpio/gpio write " + str(self.pin) + " 1"
        logging.debug("gpio_pin.on: Turning on pin %s, pin # %s", self.name, self.pin)
        return_code = subprocess.check_output(command, shell=True)
    
    def off(self):
        command = "sudo /home/pi/wiringPi/gpio/gpio write " + str(self.pin) + " 0"
        logging.debug("gpio_pin.off: Turning off pin %s, pin # %s", self.name, self.pin)
        return_code = subprocess.check_output(command, shell=True)