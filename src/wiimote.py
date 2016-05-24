#Mostly used code from these two sites
#https://code.google.com/p/raspberry-gpio-python/wiki/PWM
#http://www.cl.cam.ac.uk/projects/raspberrypi/tutorials/robot/wiimote/

import cwiid
import time
import os
import RPi.GPIO as GPIO   #The GPIO module
import picamera
import datetime
from time import sleep

#Dryrun mode for testing without motors and GPIO
DRYRUN = False
RecordingStarted = False

def calibrateTilt(acc):
    #Now left and right
    #You get a 3 tuple and the middle value is what you need.
    #Horizontal is 120.  Going right decreases the value so < 110 is steer right.  Going left increases the value so > 130 is steer left
    #SteerRightValue = 115
    #SteerLeftValue = 135
    
    return acc-8, acc+8


#A routine to control the pins
def ControlThePins(TheState):
    print "Controlling them pins:c" + TheState

    if DRYRUN == False:
        #First just turn them all off - then we work out what to do
        GPIO.output(11,False)
        GPIO.output(13,False)
        GPIO.output(19,False)
        GPIO.output(21,False)

        #Just work through the different motor states, setting the pins accordingly
        if TheState == GoForward:
            GPIO.output(11,True)
            GPIO.output(13,False)
            GPIO.output(19,True)
            GPIO.output(21,False)
        elif TheState == GoBackward:
            GPIO.output(11,False)
            GPIO.output(13,True)
            GPIO.output(19,False)
            GPIO.output(21,True)
        elif TheState == SteerLeft:
            GPIO.output(11,True)
            GPIO.output(13,False)
            GPIO.output(19,False)
            GPIO.output(21,True)
        elif TheState == SteerRight:
            GPIO.output(11,False)
            GPIO.output(13,True)
            GPIO.output(19,True)
            GPIO.output(21,False)
        elif TheState == StopIt:
            #Do nothing as we stopped all pins first thing
            pass
    else:
        print "The state: "+TheState

    #Just return
    return

#######################
#Main part of the code#
#######################

if DRYRUN == False:
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

#Constants for the system state and then an assignment
ForwardNoSteer = "FNS"
ForwardSteerLeft = "FSL"
ForwardSteerRight = "FSR"
BackwardNoSteer = "BNS"
BackwardSteerLeft = "BSL"
BackwardSteerRight = "BSR"
RotateLeft = "RL"
RotateRight = "RR"
SystemStopped = "SS"
SystemState = SystemStopped

#Control camera:
# BTN_A takes photo
# BTN_B start/stop video recording
def cameraControl():

    #if B start/stop video rec
    #if A pressed take photo

    if buttons & cwiid.BTN_A:
        print "take picture"
        with picamera.PiCamera() as camera:
            filename = "rpi_robot_" + datetime.datetime.now().strftime("%H:%M:%S") + ".jpg"
            camera.resolution = (1280, 720)
            camera.start_preview()
            #camera.exposure_compensation = 2
            #camera.exposure_mode = 'spotlight'
            #camera.meter_mode = 'matrix'
            #camera.image_effect = 'gpen'
            # Give the camera some time to adjust to conditions
            sleep(0.5)
            camera.capture(filename)
            camera.stop_preview()
    else:
        print "start/stop video"


#connecting to the Wiimote. This allows several attempts
# as first few often fail.
print 'Press 1+2 on your Wiimote now...'

wm = None
i=2
while not wm:
    try:
        wm=cwiid.Wiimote()
    except RuntimeError:
        if (i>10):
            print "Giving up connecting"
            quit()
            break
        print "Error opening wiimote connection"
        print "attempt " + str(i)
        i +=1
        #Pause for a bit
        time.sleep(0.5)


#Got here, tell the user
print "Success - we have connected!"

#set Wiimote to report button presses and accelerometer state
wm.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_ACC

#Wait a bit
time.sleep(1)

#Do a celebratory LED KITT style sweep
LoopVar = 0
while LoopVar < 3:
    #turn on leds to show connected
    wm.led = 1
    time.sleep(0.1)
    wm.led = 2
    time.sleep(0.1)
    wm.led = 4
    time.sleep(0.1)
    wm.led = 8
    time.sleep(0.1)
    #Set up for next loop
    LoopVar +=1

#Turn off the LEDs now
wm.led = 0

#Wait a bit
time.sleep(0.5)

#Do a rumble
wm.rumble = True
time.sleep(0.5)
wm.rumble = False

#Calibrate tilt
SteerRightValue, SteerLeftValue = calibrateTilt(int(wm.state['acc'][1]))
print "SteerLeftValue " + str(SteerLeftValue)
print "SteerRightValue " + str(SteerRightValue)

#Now start checking for button presses
print "Ready to receive button presses and accelerometer input"

#Loop for ever detecting

try:
    wm.led = 1
    while True:
        #Set up a button object to check
        buttons = wm.state['buttons']

        #We assess whether the Wiimote is level, left or right by assessing the accelerometer
        accVar = int(wm.state['acc'][1])

        #Check all the different possible states of button, accelerometer and system state.  First button 1 pressed and steering left
        if (buttons & cwiid.BTN_2) and (accVar > SteerLeftValue) and (SystemState != ForwardSteerLeft):
            #Tell the user
            print "Forward Steer Left"

            #Change the state to be this now
            SystemState = ForwardSteerLeft

            #Set the motor state
            ControlThePins(SteerLeft)
        elif (buttons & cwiid.BTN_2) and (accVar < SteerRightValue) and (SystemState != ForwardSteerRight):   #Button 1 pressed and steering right
            #Tell the user
            print "Forward Steer Right"

            #Change the state to be this now
            SystemState = ForwardSteerRight

            #Set the motor state
            ControlThePins(SteerRight)
        elif (buttons & cwiid.BTN_2) and (accVar >= SteerRightValue) and (accVar <= SteerLeftValue) and (SystemState != ForwardNoSteer):   #Button 1 pressed.  Acclerometer in the middle
            #Tell the user
            print "Go forward"

            #Change the state to be this now
            SystemState = ForwardNoSteer

            #Set the motor state
            ControlThePins(GoForward)
        elif (buttons & cwiid.BTN_1) and (accVar > SteerLeftValue) and (SystemState != BackwardSteerLeft):    #Backward and steering left
            #Tell the user
            print "Backward Steer Left"

            #Change the state to be this now
            SystemState = BackwardSteerLeft

            #Set the motor state
            ControlThePins(SteerLeft)
        elif (buttons & cwiid.BTN_1) and (accVar < SteerRightValue) and (SystemState != BackwardSteerRight):   #Button 2 pressed and steering right
            #Tell the user
            print "Backward Steer Right"

            #Change the state to be this now
            SystemState = BackwardSteerRight

            #Set the motor state
            ControlThePins(SteerRight)
        elif (buttons & cwiid.BTN_1) and (accVar >= SteerRightValue) and (accVar <= SteerLeftValue) and (SystemState != BackwardNoSteer):   #Button 2 pressed.  Acclerometer in the middle
            #Tell the user
            print "Go backward"

            #Change the state to be this now
            SystemState = BackwardNoSteer

            #Set the motor state
            ControlThePins(GoBackward)

        #No button pressed so we reach this else statement, see if it's because of a change of state
        elif (not(buttons & cwiid.BTN_1)) and (not(buttons & cwiid.BTN_2)) and (SystemState != SystemStopped):
            #Tell the user
            print "No buttons pressed"

            #Change the state to be this now
            SystemState = SystemStopped

            #Change the motor state to be off
            ControlThePins(StopIt)
	    
        #check if '+' and '-' are pressed to stop the program
        elif (buttons & cwiid.BTN_MINUS) and (buttons & cwiid.BTN_PLUS):
            print "+ and - pressed"
            break

        #Check other buttons when stopped
        elif ((buttons & cwiid.BTN_A) or (buttons & cwiid.BTN_B)) and (SystemState == SystemStopped):
            print "Cameracontrol"
            cameraControl()

        #Chill for a bit
        time.sleep(0.1)
except KeyboardInterrupt:
    pass

#Do a rumble and close LED
wm.rumble = True
wm.led = 0
time.sleep(0.5)
wm.rumble = False

print "Good night"

#End of the code - turn off pins then exit
ControlThePins(StopIt)
