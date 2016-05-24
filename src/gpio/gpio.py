
import time, sys, tempfile, os, string, shutil
import RPi.GPIO as gpio

_DEFAULT_DRY_RUN_MODE=True

#Set up the GPIO pins
#Get rid of warnings
GPIO.setwarnings(False)

#Set the GPIO mode
GPIO.setmode(GPIO.BOARD)

#Set the pins to be outputs
GPIO.setup(11,GPIO.OUT)
GPIO.setup(13,GPIO.OUT)
GPIO.setup(19,GPIO.OUT)
GPIO.setup(21,GPIO.OUT)

#Now we start defining some constants to use.  We have three concepts:
#1)The motor command.  Stating Forward, Backward, Left, Right, Stop
#2)The sensor position and whether a button is pressed
#3)The system state, e.g. Sys1Level, Sys1Right etc
#We determine sensor position, see if the system state has changed and if so send a new motor command

#Motor commands
GoForward = "Forward"
GoBackward = "Backward"
SteerRight = "Right"
SteerLeft = "Left"
StopIt = "Stop"

class robot_control(object):

    _instances=[]

    # Initialise the object
    def __init__(self,dryRunMode=_DEFAULT_DRY_RUN_MODE):
        if ( len(self._instances)>1 ):
            print "ERROR: You can't have more than one Arthurbot instance."
            exit(1)
        self._instances.append(self)
        self.dryRunMode=dryRunMode
        if ( self.dryRunMode ):
            print "Running in Dry Run Mode"



