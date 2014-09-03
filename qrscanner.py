#import os # Depreciated
import subprocess
from time import sleep
#import RPi.GPIO as GPIO
import photo

def FindQRCode(ScanningLEDPin, camera, nTries):
    # Hard coded image path and filename
    strpath = "/mnt/ramcache/"
    strfile = "qrtest"

    #try:
    #    GPIO.setmode(GPIO.BCM)
    #    GPIO.setup(ScanningLEDPin, GPIO.OUT)
    #except:
    #    print("GPIO Not ready")

    print "Reading data from qrcode"
    nLoop = 0
    bFound = False
    while (nLoop<nTries and bFound==False):
        #try:
        #    # Turn LED on whilst taking photo
        #    GPIO.output(ScanningLEDPin, True)
        #except:
        #    print("GPIO Not ready")

        # Grab image from camera into file
        photo.TakePhoto(camera, strpath+strfile+".jpg")
        
        # call os command to read qr data to text file
        strreadtext = strpath+strfile+".txt"
        #os.system("zbarimg -q "+strpath+strfile+".jpg > "+strreadtext)
        process = subprocess.Popen(["zbarimg -q -D /mnt/ramcache/qrtest.jpg"], stdout=subprocess.PIPE, shell=True)
        (out, err) = process.communicate()


        # out looks like "QR-code: Xuz213asdY" so you need
        # to remove first 8 characters plus whitespaces
        qr_code = None
        if len(out) > 8:
            qr_code = out[8:].strip()
            return qr_code

        #if os.path.exists(strreadtext):
        #    strqrcode = open(strreadtext, 'r').read()
        #    if strqrcode != "":
        #        # SUCCESS, Found a QR code. Send it to the 
        #        # screen and stop trying
        #        print strqrcode
        #        bFound = True
        #    else:
        #        print("Not Found")
        #else:
        #    print "QR-Code text file not found"
        
        #try:
        #    # Turn LED off after taking photo
        #    GPIO.output(ScanningLEDPin, False)
        #except:
        #    print("GPIO Not ready")
        
        # Increment Loop count and sleep for 5 seconds
        print("Try again")
        nLoop = nLoop + 1
        sleep(1)
    
    print "Finished trying to get qrcode"
    return ""
