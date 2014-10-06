import RPi.GPIO as GPIO
import time
import os
import audio
import picamera
import json
import subprocess
from arduino_comms import CommLink


class Dashboard:

    def __init__(self):

        # GPIO Pin numbers
        self.button_pin_scan = 22
        self.button_pin_power = 5
        self.button_pin_go = 27
        self.button_pin_horn = 17
        self.button_pin_manual = 4

        self.led_pin_power = 18
        self.led_pin_scanning = 23
        self.led_pin_found_qr = 24

        # initialise a previous input variable to 0 (assume button not pressed
        # last)
        self.qr_found = False
        self.time_stamp = time.time()
        self.debounce = 0.3

        # Prepare Pi Camera Module
        self.camera = Camera()

        # instantiate CommLink
        self.comm_link = CommLink(port="/dev/ttyACM0", baud_rate=9600)

        # Button States
        self.powered_off = False
        self.scanning = False
        self.going = False
        self.horn = False
        self.manual = False
        self.command_string = ""

        try:
            # Set GPIO mode and pre-config gpio ports as either IN or OUT
            GPIO.setmode(GPIO.BCM)
            # print "DEBUG-SetMode"

            # Setup GPIO port for Buttons, ready for interrupt
            GPIO.setup(
                self.button_pin_power,
                GPIO.IN,
                pull_up_down=GPIO.PUD_DOWN)
            GPIO.setup(
                self.button_pin_scan,
                GPIO.IN,
                pull_up_down=GPIO.PUD_DOWN)
            GPIO.setup(
                self.button_pin_go,
                GPIO.IN,
                pull_up_down=GPIO.PUD_DOWN)
            GPIO.setup(
                self.button_pin_horn,
                GPIO.IN,
                pull_up_down=GPIO.PUD_DOWN)
            GPIO.setup(self.button_pin_manual,
                       GPIO.IN,
                       pull_up_down=GPIO.PUD_DOWN)
            # Add callbacks for all EXCEPT the power button.
            GPIO.add_event_detect(
                self.button_pin_scan,
                GPIO.RISING,
                callback=self.scan_pressed)
            GPIO.add_event_detect(
                self.button_pin_go,
                GPIO.RISING,
                callback=self.go_pressed)
            GPIO.add_event_detect(
                self.button_pin_horn,
                GPIO.RISING,
                callback=self.horn_pressed)
            GPIO.add_event_detect(
                self.button_pin_manual,
                GPIO.RISING,
                callback=self.manual_pressed)
            # print "DEBUG-Setup and Add_Events"

            # Setup GPIO ports for LEDs
            GPIO.setup(
                self.led_pin_power,
                GPIO.OUT)
            GPIO.setup(
                self.led_pin_found_qr,
                GPIO.OUT)
            GPIO.setup(
                self.led_pin_scanning,
                GPIO.OUT)
            # Turn Power LED ON
            GPIO.output(
                self.led_pin_power,
                True)
            # Ensure Found QR LED OFF
            GPIO.output(
                self.led_pin_found_qr,
                False)
            # Ensure scanning LED OFF
            GPIO.output(
                self.led_pin_scanning,
                False)
            # print "DEBUG-Setup and Output LEDs"

        except Exception as e:
            print("Could not initialise Dashboard:")
            print e
            # clean up GPIO on CTRL+C exit
            self.shut_down()

    def start(self):
        # Main wait is for the power button, all other GPIOs are callbacks
        try:
            GPIO.wait_for_edge(self.button_pin_power, GPIO.FALLING)
            self.power_pressed(self.button_pin_power)
        except:
            self.shut_down()

    def shut_down(self):
        # Clean up GPIO settings
        print("shutting down GPIO")
        GPIO.cleanup()

    def _passes_sanity_check(self):
        time_now = time.time()
        valid_time = (time_now - self.time_stamp) >= self.debounce
        return valid_time and not self.powered_off and not self.scanning

    def _set_timestamp(self):
        self.time_stamp = time.time()

    def power_pressed(self, pin):
        """
        Handle Power button press event
        """
        if self._passes_sanity_check() and not self.going:
            self.powered_off = True
            print("Power Button pressed")
            # Turn power LED OFF
            GPIO.output(self.led_pin_power, False)
            # Issue a poweroff command
            os.system("poweroff")
            self._set_timestamp()

    def scan_pressed(self, pin):
        """
        Handle Scan button press event
        """
        print self._passes_sanity_check() and not self.going
        if self._passes_sanity_check() and not self.going:
            # Set timestamp to avoid multiple scans
            self._set_timestamp()
            # Play a sound to show that we are scanning
            audio.playSound(0)

            # Flag that we are scanning
            self.scanning = True
            print("Scan Button pressed")

            # Turn on the "scanning" LED
            GPIO.output(self.led_pin_scanning, True)
            # Ensure Found QR LED OFF
            GPIO.output(self.led_pin_found_qr, False)

            # Try to find a QR code from the camera.
            qr_code = self.camera.find_qr_code()
            if qr_code:
                # Play sound that we found one
                audio.playSound(10)
                #store it
                self.command_string = qr_code
                # Flag that we found a QR code
                self.qr_found = True
                # Ensure Found QR LED OFF
                GPIO.output(self.led_pin_found_qr, True)
            else:
                print("Couldn't find a QR code")

            # Turn off the "scanning" LED
            GPIO.output(self.led_pin_scanning, False)
            # reset scanning flag
            self.scanning = False

    # handle the button event
    def go_pressed(self, pin):
        """
        Handle Go button press event
        """
        if self._passes_sanity_check() and not self.going:
            self.going = True
            print("Go Button pressed")
            if (self.qr_found and self.command_string != ""):
                # Play a sound to show that we are scanning
                audio.playSound(10)  # play start sound

                self.comm_link.parse_command_string(self.command_string)

                # Play sound that we found one
                audio.playSound(10)

                # Success GO operation, turn LED off and flag QR found
                # as FALSE for next go
                GPIO.output(self.led_pin_found_qr, False)
                self.qr_found = False
                # Pass command to motor controller here
            else:
                print("No QR Found, scan again please")
            self.going = False
            self._set_timestamp()

    def horn_pressed(self, pin):
        """
        Handle Horn button press event
        """
        if self._passes_sanity_check() and not self.horn:
            self.horn = True
            print("horn Pressed")
            audio.playSound(11)
            self.horn = False
            self._set_timestamp()

    def manual_pressed(self, pin):
        """
        Handle Manual button press event
        """
        if self._passes_sanity_check() and not self.horn and not self.manual:
            self.manual = True
            print("manual Pressed")
            audio.playSound(11)
            self.manual = False
            self._set_timestamp()


class Camera:

    def __init__(self, location='/mnt/ramcache/', filename="qrtest"):
        # get handle on pi camera
        self.cam = picamera.PiCamera()

        self.filepath = os.path.join(
            location, "{0}.{1}".format(filename, "jpg"))

    def capture(self):
        """
        Take a single photo with the camera
        git add"""
        self.cam.capture(self.filepath)

    def find_qr_code(self, tries=10):
        """
        Attempt to capture a photo and parse a QR code from it.
        returns None or string
        """
        print "Attempting to capture QR code"

        for i in range(tries):
            # grab a photo from the camera
            print "Attempt {0}:".format(i)
            self.capture()

            # pass it to zbarimg to attempt to read qr code
            process = subprocess.Popen(
                ["zbarimg -q -D {0}".format(self.filepath)],
                stdout=subprocess.PIPE,
                shell=True)
            (out, err) = process.communicate()
            print "zbarimg output: {0}".format(out)
            # out looks like "QR-code: Xuz213asdY" so you need
            # to remove first 8 characters plus whitespaces
            if len(out) > 8:
                return self.parse_out_command(out[8:].strip())

            # Couldn't parse a qr code
            # sleep and retry
            print("No QR code found - sleeping")
            time.sleep(1)

        print "Couldn't parse QR code - bailing"
        return None

    def parse_out_command(self, qr_code_content):
        """
        Parse instruction JSON content
        """
        try:
            return json.loads(qr_code_content)
        except ValueError:
            print "Couldn't parse instruction as valid JSON"
            return None
