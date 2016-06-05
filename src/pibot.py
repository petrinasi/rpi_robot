#!/usr/bin/env python
# ArthurBot, a module for controlling an L293D-based robot 
# from a Raspberry Pi.
# Andrew Oakley www.aoakley.com
# Public Domain 2013-09-13

# The L293D chip typically controls two DC motors.
# An L293D-based robot typically has two tracks, like
# an army tank. Alternatively it may have two drive wheels
# and one or more free-spinning castors or skis/skids, like
# a Logo turtle. Either way, it has two motors, one on the
# left and one on the right.
# Think of a BigTrak toy, Johnny Five from "Short Circuit"
# or a bomb disposal robot.

# Each motor can spin forward or backward.
# Turning left or right is achieved by having one side
# go forward whilst the other goes backward, which
# spins the robot around like a tank.

# The robot may also speak (using the espeak Linux program)
# and take a photo (using the Raspberry Pi camera)

#### Imports ####

# Import prerequisite modules
import time, sys, tempfile, os, string, shutil
import RPi.GPIO as gpio

#### Constants ####

# Here's where you can fine-tune how this module works, without
# messing up the program itself.

# If Dry Run Mode is set, then instead of the GPIO pins being
# turned on/off, the program will instead just print messages
# to the system standard output. Handy for practice programs.
# This constant defines whether dry run mode is the default or not.
# You can override this when instantiating the ArthurBot object.
_DEFAULT_DRY_RUN_MODE=False

# Two motors with two directions each = four GPIO pins
# The L293D chip also has an "enable" pin - a dead man's handle;
# if the enable pin is off, the other pins are ignored.
# Here we define which GPIO pins do what
_GPIO_PIN_RIGHT_MOTOR_FORWARD=11
_GPIO_PIN_RIGHT_MOTOR_BACKWARD=13
_GPIO_PIN_LEFT_MOTOR_FORWARD=19
_GPIO_PIN_LEFT_MOTOR_BACKWARD=21
# _GPIO_PIN_ENABLE=22

# Next we define how long a "step" is. A step is defined
# in terms of milliseconds (thousandths of a second).
# So if a step is 500 milliseconds, then commanding the
# robot to go forward for 2 steps would result in both
# motors being turned on in the forward direction for
# 1 second (2x500ms) and then turned off.
# Note that neither Python nor Raspbian are "real-time", so
# it's pointless trying to be accurate to less than ten
# milliseconds or so.
# Step duration is used for forward and backward commands.
_STEP_DURATION=1000

# Now the turn duration. This is used for the left and right
# commands. Again, this is milliseconds. You could fine-tune
# this so it matches a quarter-turn, or 45 degrees, or
# whatever suits your project. I doubt you'll get much finer
# control than approximately 15 degrees. If you can hand-build
# a robot that can travel in a perfect square, well done you!
_TURN_DURATION=1600

# "Bias" is a tweak for where you have one motor (or
# gearing) which is slightly stronger than the other - which
# is my case using very old 1970s/1980s Lego motors. This
# results in repeated forward steps actually turning
# slightly off to one side. We will compensate by letting the
# left motor run for slightly shorter or longer than the
# right motor. The right motor will always run for DURATION,
# whilst the left motor will run for DURATION+BIAS.
# Don't have the bias greater than the duration - your robot
# will drag itself around in circles.
# Bias is applied to backward, left and right too.
# Veering right? Use a negative value.
# Veering left? Use a positive value.
# Value is in milliseconds. Try 100 for starters.
_STEP_BIAS=0
_TURN_BIAS=0

# That's the end of the configuration. You should not need
# to change anything past this point. Of course, you *can*
# change anything you like, but changing things past this
# point makes it much more likely to go wrong. In particular,
# make sure you always turn the motors off at the end - 
# otherwise your precious buddy might throw himself off a
# table, down some stairs, or against a wall.

#### One-time setup ####

# Set up the GPIO pins, referring to the constants
gpio.setwarnings(False)
gpio.setmode(gpio.BOARD)
gpio.setup(_GPIO_PIN_RIGHT_MOTOR_FORWARD, gpio.OUT)
gpio.setup(_GPIO_PIN_RIGHT_MOTOR_BACKWARD, gpio.OUT)
gpio.setup(_GPIO_PIN_LEFT_MOTOR_FORWARD, gpio.OUT)
gpio.setup(_GPIO_PIN_LEFT_MOTOR_BACKWARD, gpio.OUT)
# gpio.setup(_GPIO_PIN_ENABLE, gpio.OUT)

#### Objects ####

class PiBot(object):
    # We need to keep a track of instances,
    # since we should only ever have one.
    # You could adapt this program to have more
    # - the Raspberry Pi has enough GPIO pins -
    # but you'd need to change this code a lot.
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

    # Move forward so many units
    # To move right, we put the both motors into forward
    def forward(self,units):
        if ( self.dryRunMode ):
            for step in range(0,units):
                print "Forward"
        else:
            for step in range(0,units):
                print "Forward"
                gpio.output(_GPIO_PIN_LEFT_MOTOR_FORWARD, True)
                gpio.output(_GPIO_PIN_LEFT_MOTOR_BACKWARD, False)
                gpio.output(_GPIO_PIN_RIGHT_MOTOR_FORWARD, True)
                gpio.output(_GPIO_PIN_RIGHT_MOTOR_BACKWARD, False)
                self._waitStepPreBias()
                if ( _STEP_BIAS < 0 ):
                    # We're veering right - turn off
                    # the left motor early
                    gpio.output(_GPIO_PIN_LEFT_MOTOR_FORWARD, False)
                self._waitStepBias()
                # Turn off the right motor bang on time
                gpio.output(_GPIO_PIN_RIGHT_MOTOR_FORWARD, False)
                if ( _STEP_BIAS > 0 ):
                    # We're veering left - leave the
                    # left motor running a bit longer
                    self._waitStepBias()
                # Now turn off the left motor, even if
                # we already turned it off early
                gpio.output(_GPIO_PIN_LEFT_MOTOR_FORWARD, False)
            # Turn off all pins
            self._stop()

    # Move backward so many units
    def backward(self,units):
        if ( self.dryRunMode ):
            for step in range(0,units):
                print "Backward"
                self._waitStepPreBias()
                self._waitStepBias()
        else:
            for step in range(0,units):
                print "Backward"
                gpio.output(_GPIO_PIN_LEFT_MOTOR_FORWARD, False)
                gpio.output(_GPIO_PIN_LEFT_MOTOR_BACKWARD, True)
                gpio.output(_GPIO_PIN_RIGHT_MOTOR_FORWARD, False)
                gpio.output(_GPIO_PIN_RIGHT_MOTOR_BACKWARD, True)
                self._waitStepPreBias()
                if ( _STEP_BIAS < 0 ):
                    # Right motor is a bit weak - turn off
                    # the left motor early
                    gpio.output(_GPIO_PIN_LEFT_MOTOR_BACKWARD, False)
                self._waitStepBias()
                # Turn off the right motor bang on time
                gpio.output(_GPIO_PIN_RIGHT_MOTOR_BACKWARD, False)
                if ( _STEP_BIAS > 0 ):
                    # Left motor is a bit weak - leave the
                    # left motor running a bit longer
                    self._waitStepBias()
                # Now turn off the left motor, even if
                # we already turned it off early
                gpio.output(_GPIO_PIN_LEFT_MOTOR_BACKWARD, False)
            # Turn off all pins
            self._stop()

    # Move right so many units
    # To move right, we put the right motor into reverse
    # and put the left motor into forward. That spins the
    # robot clockwise, as viewed from above.
    def right(self,units):
        if ( self.dryRunMode ):
            for step in range(0,units):
                print "Right"
                self._waitTurnPreBias()
                self._waitTurnBias()
        else:
            for step in range(0,units):
                print "Right"
                gpio.output(_GPIO_PIN_LEFT_MOTOR_FORWARD, True)
                gpio.output(_GPIO_PIN_LEFT_MOTOR_BACKWARD, False)
                gpio.output(_GPIO_PIN_RIGHT_MOTOR_FORWARD, False)
                gpio.output(_GPIO_PIN_RIGHT_MOTOR_BACKWARD, True)
                self._waitTurnPreBias()
                if ( _TURN_BIAS < 0 ):
                    # Right motor is a bit weak - turn off
                    # the left motor early
                    gpio.output(_GPIO_PIN_LEFT_MOTOR_FORWARD, False)
                self._waitTurnBias()
                # Turn off the right motor bang on time
                gpio.output(_GPIO_PIN_RIGHT_MOTOR_BACKWARD, False)
                if ( _TURN_BIAS > 0 ):
                    # Left motor is a bit weak - leave the
                    # left motor running a bit longer
                    self._waitTurnBias()
                # Now turn off the left motor, even if
                # we already turned it off early
                gpio.output(_GPIO_PIN_LEFT_MOTOR_FORWARD, False)
            # Turn off all pins
            self._stop()

    # Move left so many units
    # To move left, we put the right motor into forward
    # and put the left motor into reverse. That spins the
    # robot anti-clockwise, as viewed from above.
    def left(self,units):
        if ( self.dryRunMode ):
            for step in range(0,units):
                print "Left"
        else:
            for step in range(0,units):
                print "Left"
                gpio.output(_GPIO_PIN_LEFT_MOTOR_FORWARD, False)
                gpio.output(_GPIO_PIN_LEFT_MOTOR_BACKWARD, True)
                gpio.output(_GPIO_PIN_RIGHT_MOTOR_FORWARD, True)
                gpio.output(_GPIO_PIN_RIGHT_MOTOR_BACKWARD, False)
                self._waitTurnPreBias()
                if ( _TURN_BIAS < 0 ):
                    # Right motor is a bit weak - turn off
                    # the left motor early
                    gpio.output(_GPIO_PIN_LEFT_MOTOR_BACKWARD, False)
                self._waitTurnBias()
                # Turn off the right motor bang on time
                gpio.output(_GPIO_PIN_RIGHT_MOTOR_FORWARD, False)
                if ( _TURN_BIAS > 0 ):
                    # Left motor is a bit weak - leave the
                    # left motor running a bit longer
                    self._waitTurnBias()
                # Now turn off the left motor, even if
                # we already turned it off early
                gpio.output(_GPIO_PIN_LEFT_MOTOR_BACKWARD, False)
            # Turn off all pins
            self._stop()

    # Stop all the motors and turn off the enable pin
    # The movement methods should all do this when they exit
    # anyway, but this provides a belt-and-braces stop
    # that might be useful as part of an try/except error
    # handler.
    def allStop(self):
            if ( self.dryRunMode ):
                print "All Stop"
            else:
                gpio.output(_GPIO_PIN_LEFT_MOTOR_FORWARD, False)
                gpio.output(_GPIO_PIN_LEFT_MOTOR_BACKWARD, False)
                gpio.output(_GPIO_PIN_RIGHT_MOTOR_FORWARD, False)
                gpio.output(_GPIO_PIN_RIGHT_MOTOR_BACKWARD, False)
    

    # Wait for one step minus the bias
    def _waitStepPreBias(self):
        time.sleep((_STEP_DURATION-abs(_STEP_BIAS))/1000.0)
        pass

    # Wait for the step bias
    def _waitStepBias(self):
        time.sleep(abs(_STEP_BIAS)/1000.0)
        pass

    # Wait for one turn minus the bias
    def _waitTurnPreBias(self):
        time.sleep((_TURN_DURATION-abs(_TURN_BIAS))/1000.0)
        pass

    # Wait for the turn bias
    def _waitTurnBias(self):
        time.sleep(abs(_TURN_BIAS)/1000.0)
        pass

    def _stop(self):
        gpio.output(_GPIO_PIN_LEFT_MOTOR_FORWARD, False)
        gpio.output(_GPIO_PIN_LEFT_MOTOR_BACKWARD, False)
        gpio.output(_GPIO_PIN_RIGHT_MOTOR_FORWARD, False)
        gpio.output(_GPIO_PIN_RIGHT_MOTOR_BACKWARD, False)

    def takePhoto(self,destination=os.getcwd(),fileprefix="arthurbot"):
        if ( self.dryRunMode ):
            print "Take photo and save it to " + destination
        else:
            photopath=tempfile.gettempdir() + '/' + fileprefix + '-' + time.strftime("%Y%m%d-%a-%H%M-%S") + '.jpg'
            os.system ( "raspistill -n -t 500 -w 1024 -h 768 -e jpg -q 75 -o \"%s\"" % photopath )
            shutil.copy(photopath,destination)

    def say(self,message):
        if ( self.dryRunMode ):
            print "Say: " + message
            time.sleep(2)
        else:
            print "Say: " + message
            os.system ('espeak -ven-uk -p 66 -a 200 -s 150 -g 10 "' + repr(message) + '" 2>>/dev/null')
