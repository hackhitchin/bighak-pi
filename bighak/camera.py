import picamera
import os
import json
import time
import subprocess


class Camera:

    def __init__(self, location='/mnt/ramcache/', filename="qrtest"):
        # get handle on pi camera
        self.cam = picamera.PiCamera()
        full_filename = "{0}.{1}".format(filename, "jpg")
        self.filepath = os.join([self.location, full_filename])

    def capture(self):
        """
        Take a single photo with the camera
        """
        self.cam.capture(os.path.join([self.location, self.filename]))

    def find_qr_code(self, tries=10):
        """
        Attempt to capture a photo and parse a QR code from it.
        returns None or string
        """
        print "Reading data from qrcode"

        for i in range(tries):
            # grab a photo from the camera
            self.capture()

            # pass it to zbarimg to attempt to read qr code
            cmd = "zbarimg -q -D {0}".format(self.filepath)
            process = subprocess.Popen([cmd],
                                       stdout=subprocess.PIPE,
                                       shell=True)
            out, err = process.communicate()

            # out looks like "QR-code: Xuz213asdY" so you need
            # to remove first 8 characters plus whitespaces
            if len(out) > 8:
                return self.parse_out_command(out[8:].strip())

            # Couldn't parse a qr code
            # sleep and retry
            time.sleep(1)

        print "Couldn't parse QR code - bailing"
        return None

    def parse_out_command(qr_code_content):
        """
        Parse instruction JSON content
        """
        try:
            return json.loads(qr_code_content)
        except ValueError:
            print "Couldn't parse instruction as valid JSON"
            return None
