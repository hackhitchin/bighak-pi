import RPi.GPIO as GPIO
import time
import os
import audio
import picamera
import json
import serial
import subprocess


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

            # Main wait is for the power button, all other GPIOs are callbacks
            GPIO.wait_for_edge(self.button_pin_power, GPIO.FALLING)
            self.power_pressed(self.button_pin_power)

        except:
            print("Exception Caught")
            GPIO.cleanup()       # clean up GPIO on CTRL+C exit

        # Clean up GPIO settings
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
    def go_pressed(self, pin):
        """
        Handle Go button press event
        """
        if self._passes_sanity_check() and not self.going:
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

        self.filepath = os.join(
            [self.location, "{0}.{1}".format(filename, "jpg")])

    def capture(self):
        """
        Take a single photo with the camera
        git add"""
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
            process = subprocess.Popen(
                ["zbarimg -q -D {0}".format(self.filepath)],
                stdout=subprocess.PIPE,
                shell=True)
            (out, err) = process.communicate()

            # out looks like "QR-code: Xuz213asdY" so you need
            # to remove first 8 characters plus whitespaces
            if len(out) > 8:
                return self.parse_out_command(out[8:].strip())

            # Couldn't parse a qr code
            # sleep and retry
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


class CommLink:

    def __init__(self, port=None, baud_rate=9600):
        self.serial_port = port
        self.baud_rate = baud_rate
        self.serial_link = serial.Serial(self.port, self.baud_rate)

        self.INTERVAL = 0.5  # In Seconds
        self.FB_SECONDS = 1.0
        self.LR_SECONDS = 0.125
        self.PZ_SECONDS = 0.5

    def _get_command_length(self, command_verb):
        interval_map = [
            (['F', 'B'], self.FB_SECONDS),
            (['L', 'R'], self.LR_SECONDS),
            (['P', 'Z'], self.PZ_SECONDS),
        ]

        # generate a list of the 2nd tuple items where the
        # command_verb is present in the first tuple item
        match_list = [item[1] for item in interval_map
                      if command_verb.upper() in item[0]]
        # return the first item, or none if any
        return match_list[0] if match_list else None

    def repeat_send(self, command_verb, nSeconds, INTERVAL):
        # Send a single char repeatedly at a specific
        # interval for a specific length of time.
        # Have to play fireing sound here as it sounds as it lights LED
        if (command_verb == 'P'):
            # Play a sound to show that we are scanning
            audio.playSound(11)

        if (command_verb == 'Z'):
            LASER_REPEATS = 5
            # Uppercase 'Z' to turn LED ON
            print(command_verb * LASER_REPEATS)
            self.serial_link.write('Z' * LASER_REPEATS)
            # Play sound
            audio.playSound(11)
            # Lower case 'z' to turn LED OFF
            serial.write('z' * LASER_REPEATS)
            print('z' * LASER_REPEATS)
            time.sleep(0.3)
        else:
            while (nSeconds > 0.0):
                print(command_verb)
                self.serial_link.write(command_verb)
                time.sleep(INTERVAL)
                nSeconds = nSeconds - INTERVAL

    def send_command_string(self, command_verb, command_value):
        # uppercase the command_verb
        command_verb = command_verb.upper()

        # command interval
        command_length = self._get_command_length(command_value)

        # Simply write to the serial device
        for i in range(command_value):
            self.repeat_send(command_verb, command_length, self.INTERVAL)

    def parse_command_string(self, command_string):
        pause_length = 0.5
        # our commands are always 3 char where:
        # [0] is verb, [1][2] is the value (left padded)
        chunk_length = 3

        command_list = [command_string[i:i + chunk_length] for i in
                        range(0, len(command_string), chunk_length)]

        for command in command_list:
            # decompose command into command_verb & command_value
            command_verb, command_value = command[:1], command[1:]

            # if for some reason we have an incomplete command,
            # command value will be a zero length string
            # in that case, skip it
            if command_value != "":
                # pause
                time.sleep(pause_length)
                # send the command (cast command value to int first)
                self.send_command_string(command_verb, int(command_value))
