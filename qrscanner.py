import subprocess
from time import sleep
import photo

def FindQRCode(ScanningLEDPin, camera, nTries):
    # Hard coded image path and filename
    strpath = "/mnt/ramcache/"
    strfile = "qrtest"

    print "Reading data from qrcode"
    nLoop = 0
    bFound = False
    while (nLoop<nTries and bFound==False):

        # Grab image from camera into file
        photo.take_photo(camera, strpath+strfile+".jpg")
        
        # call os command to read qr data to text file
        strreadtext = strpath+strfile+".txt"
        process = subprocess.Popen(["zbarimg -q -D /mnt/ramcache/qrtest.jpg"], stdout=subprocess.PIPE, shell=True)
        (out, err) = process.communicate()

        # out looks like "QR-code: Xuz213asdY" so you need
        # to remove first 8 characters plus whitespaces
        qr_code = None
        if len(out) > 8:
            qr_code = out[8:].strip()
            return qr_code

        # Increment Loop count and sleep for 5 seconds
        print("Try again")
        nLoop = nLoop + 1
        sleep(1)
    
    print "Finished trying to get qrcode"
    return ""
