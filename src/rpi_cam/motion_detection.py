#!/usr/bin/python

    # original script by brainflakes, improved by pageauc, peewee2 and Kesthal
    # www.raspberrypi.org/phpBB3/viewtopic.php?f=43&t=45235

    # You need to install PIL to run this script
    # type "sudo apt-get install python-imaging-tk" in an terminal window to do this

    # play with it KLL
    # /home/pi/python_cam/picam4.py
    # rev b with dropbox, ftp, email options
    
import StringIO
import subprocess
import os
import time
from datetime import datetime
from PIL import Image

# Import smtplib to provide email functions
import smtplib
#from email.mime.text import MIMEText

    # Motion detection settings:
    # Threshold          - how much a pixel has to change by to be marked as "changed"
    # Sensitivity        - how many changed pixels before capturing an image, needs to be higher if noisy view
    # ForceCapture       - whether to force an image to be captured every forceCaptureTime seconds, values True or False
    # filepath           - location of folder to save photos
    # filenamePrefix     - string that prefixes the file name for easier identification of files.
    # diskSpaceToReserve - Delete oldest images to avoid filling disk. How much byte to keep free on disk.
    # cameraSettings     - "" = no extra settings; "-hf" = Set horizontal flip of image; "-vf" = Set vertical flip; "-hf -vf" = both horizontal and vertical flip
threshold   = 10
sensitivity = 140
rotation    = 180               # KLL camera mounting

forceCapture = True
forceCaptureTime = 1 * 60 # every minute for webserver* 60      # Once an hour

        # info by print
info_print = True

        # store image files to temp fs 
filepath       = "/home/pi/picam"
filenamePrefix = "RPICAM"
file_typ       = ".jpg"

prg_msg = "boot"  # used to get more info in print when a picture is made

        # option and the newest one is referred to by a linkfile in same dir
link_tolastpicture = True       # KLL 
lfile = "last.jpg"              # KLL make it as symlink

        # option send file to DROPBOX, ! very long API procedure !
send_dropbox = False            # KLL test files in drop_box and to PC

        # option send ( or move ) file to a FTP server 
send_ftp     = False             # KLL FTP
ftp_remotepath = "/usb1_1/rpi/"                         # a USB stick
ftp_account = "kll-ftp:*****@192.168.1.1:2121"          # in my router: USER:PASSWORD@SERVER:PORT

#wput_option = " -R"            # opt "-R" for move file
wput_option = " "

        # option email
send_email_enable = False
# Define email addresses to use
addr_to   = 'kllsamui@gmail.com'
addr_from = 'kllsamui@gmail.com'

# Define SMTP email server details
GMAIL_USER = 'kllsamui@gmail.com'
GMAIL_PASS = '*****'
SMTP_SERVER = 'smtp.gmail.com:587'

# email control
emaildeltaTime = 1 * 60 * 60                    # send mail again only after ... hour
last_send = time.time() - emaildeltaTime        # so first picture ( at start / boot ) also makes a email

# temp fs ?100MB? should keep 10MB for other program to use
diskSpaceToReserve = 10 * 1024 * 1024   # Keep 10 mb free on disk
# with 95*1024*1024 == 99614720 it deletes all ??
# delets always a file each time is makes a new one! 
# with 90*1024*1024 == 94371840 it deletes (one) the oldest.


cameraSettings = ""

    # settings of the photos to save
saveWidth   = 1296
saveHeight  = 972
saveQuality = 15 # Set jpeg quality (0 to 100)

    # Test-Image settings
testWidth = 100
testHeight = 75

    # this is the default setting, if the whole image should be scanned for changed pixel
testAreaCount = 1
testBorders = [ [[1,testWidth],[1,testHeight]] ]  # [ [[start pixel on left side,end pixel on right side],[start pixel on top side,stop pixel on bottom side]] ]
    # testBorders are NOT zero-based, the first pixel is 1 and the last pixel is testWith or testHeight

    # with "testBorders", you can define areas, where the script should scan for changed pixel
    # for example, if your picture looks like this:
    #
    #     ....XXXX
    #     ........
    #     ........
    #
    # "." is a street or a house, "X" are trees which move arround like crazy when the wind is blowing
    # because of the wind in the trees, there will be taken photos all the time. to prevent this, your setting might look like this:

    # testAreaCount = 2
    # testBorders = [ [[1,50],[1,75]], [[51,100],[26,75]] ] # area y=1 to 25 not scanned in x=51 to 100

    # even more complex example
    # testAreaCount = 4
    # testBorders = [ [[1,39],[1,75]], [[40,67],[43,75]], [[68,85],[48,75]], [[86,100],[41,75]] ]

    # in debug mode, a file debug.bmp is written to disk with marked (?GREEN?) changed pixel an with marked border of scan-area
    # debug mode should only be turned on while testing the parameters above
debugMode = False # False or True
debug_bmp = "debug.bmp"


def send_email(recipient, subject, text):
        smtpserver = smtplib.SMTP(SMTP_SERVER)
        smtpserver.ehlo()
        smtpserver.starttls()
        smtpserver.ehlo
        smtpserver.login(GMAIL_USER, GMAIL_PASS)
        header = 'To:' + recipient + '\n' + 'From: ' + GMAIL_USER
        header = header + '\n' + 'Subject:' + subject + '\n'
        msg = header + '\n' + text + ' \n\n'
        smtpserver.sendmail(GMAIL_USER, recipient, msg)
        smtpserver.close()

    # Capture a small test image (for motion detection)
def captureTestImage(settings, width, height):
        command = "raspistill %s -w %s -h %s -t 200 -e bmp -n -o -" % (settings, width, height)
        imageData = StringIO.StringIO()
        imageData.write(subprocess.check_output(command, shell=True))
        imageData.seek(0)
        im = Image.open(imageData)
        buffer = im.load()
        imageData.close()
        return im, buffer

    # Save a full size image to disk
def saveImage(settings, width, height, quality, diskSpaceToReserve):
        global last_send #it is read and set here
        keepDiskSpaceFree(diskSpaceToReserve)
        #time = datetime.now()    # KLL bad to call this variable time !
        t_now = datetime.now()
        s_now = "-%04d%02d%02d-%02d%02d%02d" % (t_now.year, t_now.month, t_now.day, t_now.hour, t_now.minute, t_now.second)
        filename = filenamePrefix + s_now + file_typ
        fullfilename = filepath + filename
        lastfilename = filepath + lfile
        subprocess.call("raspistill %s -w %s -h %s -t 200 -e jpg -q %s -n -rot %s -o %s" % (settings, width, height, quality, rotation, fullfilename), shell=True)
        if info_print :
                print " %s captured %s" % (prg_msg,fullfilename)

        if link_tolastpicture : # tested ok
                try:
                        os.remove(lastfilename)
                except:
                        pass # not exist at first start
                os.symlink(fullfilename,lastfilename)
#               os.chmod(lastfilename,stat.S_IXOTH)    #stat.S_IRWXG
                pass

        if send_dropbox : # tested ok
                subprocess.call("/home/pi/python_cam/dropbox_uploader.sh upload %s /RPICAM1/" % (fullfilename), shell=True)
                if info_print :
                        print "upload dropbox"
                pass

        if send_ftp :  # only works from that dir! # tested ok
                if info_print :
                        wput_opt = wput_option
                        pass
                else :
                        wput_opt = wput_option+" -q" # quiet
                        pass
                os.chdir(filepath)
                subprocess.call("wput %s %s ftp://%s%s" % (wput_opt,filename,ftp_account,ftp_remotepath), shell=True)
                os.chdir("/")
                if info_print :
                        print "upload ftp"
                pass

        if send_email_enable :
                #print 'now: %s' % (str( time.time()))
                #print 'last_send: %s' % (str(last_send))
                #print 'emaildeltaTime: %s' % (str( emaildeltaTime ))
                if time.time() - last_send > emaildeltaTime :
                        emailsubject = 'from RPI CAM1: '
                        emailtext    = 'motion detect: ' + fullfilename
                        send_email(addr_to, emailsubject , emailtext)
                        last_send = time.time()
                        if info_print :
                                print "send email"
                        pass
                pass

    # Keep free space above given level
def keepDiskSpaceFree(bytesToReserve):
        if (getFreeSpace() < bytesToReserve):
            os.chdir(filepath)     #KLL now works better
            for dfilename in sorted(os.listdir(filepath)):
                if dfilename.startswith(filenamePrefix) and dfilename.endswith(file_typ):
                    print "Deleted %s to avoid filling disk" % (dfilename)
                    os.remove(dfilename)
                    if (getFreeSpace() > bytesToReserve):
                        os.chdir("/")  # KLL
                        return

    # Get available disk space
def getFreeSpace():
        st = os.statvfs(filepath)
        du = st.f_bavail * st.f_frsize
        #print " free space: %s " % (du)
        return du

#_________ main ________________________________________________________________________________________
    # Get first image
if info_print :
        print('get first image')
image1, buffer1 = captureTestImage(cameraSettings, testWidth, testHeight)

    # Reset last capture time
lastCapture = time.time()

if info_print :
        print('start loop')   # and take a very first picture to see start time ...
        

saveImage(cameraSettings, saveWidth, saveHeight, saveQuality, diskSpaceToReserve)
prg_msg = "motion"

while (True):

        # Get comparison image
        image2, buffer2 = captureTestImage(cameraSettings, testWidth, testHeight)

        # Count changed pixels
        changedPixels = 0
        takePicture = False

        if (debugMode): # in debug mode, save a bitmap-file with marked changed pixels and with visible testarea-borders
            debugimage = Image.new("RGB",(testWidth, testHeight))
            debugim = debugimage.load()

        for z in xrange(0, testAreaCount): # = xrange(0,1) with default-values = z will only have the value of 0 = only one scan-area = whole picture
            for x in xrange(testBorders[z][0][0]-1, testBorders[z][0][1]): # = xrange(0,100) with default-values
                for y in xrange(testBorders[z][1][0]-1, testBorders[z][1][1]):   # = xrange(0,75) with default-values; testBorders are NOT zero-based, buffer1[x,y] are zero-based (0,0 is top left of image, testWidth-1,testHeight-1 is botton right)
                    if (debugMode):
                        debugim[x,y] = buffer2[x,y]
                        if ((x == testBorders[z][0][0]-1) or (x == testBorders[z][0][1]-1) or (y == testBorders[z][1][0]-1) or (y == testBorders[z][1][1]-1)):
                            # print "Border %s %s" % (x,y)
                            debugim[x,y] = (0, 0, 255) # in debug mode, mark all border pixel to blue
                    # Just check green channel as it's the highest quality channel
                    pixdiff = abs(buffer1[x,y][1] - buffer2[x,y][1])
                    if pixdiff > threshold:
                        changedPixels += 1
                        if (debugMode):
                            debugim[x,y] = (0, 255, 0) # in debug mode, mark all changed pixel to green
                    # Save an image if pixels changed
                    if (changedPixels > sensitivity):
                        takePicture = True # will shoot the photo later
                    if ((debugMode == False) and (changedPixels > sensitivity)):
                        break  # break the y loop
                if ((debugMode == False) and (changedPixels > sensitivity)):
                    break  # break the x loop
            if ((debugMode == False) and (changedPixels > sensitivity)):
                break  # break the z loop

        if (debugMode):
            debugimage.save(filepath + debug_bmp) # save debug image as bmp
            print "debug.bmp saved, %s changed pixel" % changedPixels
        # else:
        #     print "%s changed pixel" % changedPixels

        # Check force capture
        if forceCapture:
                #print 'now: %s' % (str( time.time()))
                #print 'lastCapture: %s' % (str(lastCapture))
                #print 'forceCaptureTime: %s' % (str( forceCaptureTime ))
                if time.time() - lastCapture > forceCaptureTime:
                        takePicture = True
                        prg_msg = "force"

        if takePicture:
            lastCapture = time.time()
            saveImage(cameraSettings, saveWidth, saveHeight, saveQuality, diskSpaceToReserve)
            prg_msg = "motion"

        # Swap comparison buffers
        image1 = image2
        buffer1 = buffer2
