import RPi.GPIO as GPIO
import time
import qrscanner
import photo
import os
import audio
import parseQR
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
        self.camera = None
        try:
            self.camera = photo.prepare_camera()
        except:
            raise("Camera Not Ready")

        # instantiate CommLink
        comm_link = CommLink(port="/dev/ttyACM0", baud_rate=9600)

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
            GPIO.setup(self.button_pin_power, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            GPIO.setup(self.button_pin_scan, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            GPIO.setup(self.button_pin_go, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            GPIO.setup(self.button_pin_horn, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            GPIO.setup(self.button_pin_manual, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            # Add callbacks for all EXCEPT the power button.
            GPIO.add_event_detect(
                self.button_pin_scan, GPIO.RISING, callback=scan_pressed)
            GPIO.add_event_detect(
                self.button_pin_go, GPIO.RISING, callback=go_pressed)
            GPIO.add_event_detect(
                self.button_pin_horn, GPIO.RISING, callback=horn_pressed)
            GPIO.add_event_detect(
                self.button_pin_manual, GPIO.RISING, callback=manual_pressed)
            # print "DEBUG-Setup and Add_Events"

            # Setup GPIO ports for LEDs
            GPIO.setup(self.led_pin_power, GPIO.OUT)
            GPIO.setup(self.led_pin_found_qr, GPIO.OUT)
            GPIO.setup(self.led_pin_scanning, GPIO.OUT)
            GPIO.output(self.led_pin_power, True)  # Turn Power LED ON
            GPIO.output(self.led_pin_found_qr, False)  # Ensure Found QR LED OFF
            GPIO.output(self.led_pin_scanning, False)  # Ensure scanning LED OFF
            # print "DEBUG-Setup and Output LEDs"

            # Main wait is for the power button, all other GPIOs are callbacks
            GPIO.wait_for_edge(self.button_pin_power, GPIO.FALLING)
            self.power_pressed(self.button_pin_power)

        except:
            print("Exception Caught")
            GPIO.cleanup()       # clean up GPIO on CTRL+C exit

        # Clean up GPIO settings
        GPIO.cleanup()

    def _passes_sanity_check():
        time_now = time.time()
        valid_time = (time_now - self.time_stamp) >= self.debounce
        return valid_time and not self.powered_off and not self.scanning

    def _set_timestamp():
        self.time_stamp = time.time()


    def power_pressed(pin):
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

    def scan_pressed(pin):
        """
        Handle Scan button press event
        """
        if self._passes_sanity_check() and not self.going:
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
            QRCode = qrscanner.FindQRCode(
                self.led_pin_scanning, self.camera, 10)
            if (QRCode != ""):
                # Play sound that we found one
                audio.playSound(10)

                # Found a QR Code, Strip out the command portion of the string
                command_string = parseQR.parseOutCommand(QRCode)
                # Flag that we found a QR code
                qr_found = True
                # Ensure Found QR LED OFF
                GPIO.output(led_pin_found_qr, True)

            # Turn off the "scanning" LED
            GPIO.output(led_pin_scanning, False)
            # reset scanning flag
            self.scanning = False
            self._set_timestamp()

    # handle the button event
    def go_pressed(pin):
        """
        Handle Go button press event
        """
        if self._passes_sanity_check()  and not self.going:
            self.going = True
            print("Go Button pressed")
            if (self.qr_found == True and self.command_string != ""):
                # Play a sound to show that we are scanning
                audio.playSound(10)  # play start sound

                self.comm_link.parsecommand_string(command_string)

                # Play sound that we found one
                audio.playSound(10)

                # Success GO operation, turn LED off and flag QR found as FALSE for
                # next go
                GPIO.output(led_pin_found_qr, False)
                self.qr_found = False
                # Pass command to motor controller here
            else:
                print("No QR Found, scan again please")
            self.going = False
            self._set_timestamp()

    def horn_pressed(pin):
        """
        Handle Horn button press event
        """
        if self._passes_sanity_check() and not self.horn:
            self.horn = True
            print("horn Pressed")
            audio.playSound(11)
            self.horn = False
            self._set_timestamp()

    def manual_pressed(pin):
        """
        Handle Manual button press event
        """
        if self._passes_sanity_check() and not self.horn and not self.manual:
            self.manual = True
            print("manual Pressed")
            audio.playSound(11)
            self.manual = False
            self._set_timestamp()
