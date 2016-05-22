import picamera
import datetime
from time import sleep

camera = picamera.PiCamera()

def takePicture():
    filename = "rpi_robot" + datetime.datetime.now().strftime("%H:%M:%S") + ".jpg"
    camera.resolution = (1280, 720)
    camera.start_preview()
    #camera.exposure_compensation = 2
    #camera.exposure_mode = 'spotlight'
    #camera.meter_mode = 'matrix'
    #camera.image_effect = 'gpen'
    # Give the camera some time to adjust to conditions
    sleep(2)
    camera.capture(filename)
    camera.stop_preview()

def startVideo():
    filename = "rpi_robot" + datetime.datetime.now().strftime("%H:%M:%S") + ".h264"
    camera.start_recording(filename)
    sleep(5)
    camera.stop_recording()

def stopVideo():
    camera.stop_recording()
