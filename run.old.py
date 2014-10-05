import RPi.GPIO as GPIO
import time
import qrscanner
import photo
import os
import audio
import parseQR
import arduino_comms

# GPIO Pin numbers
button_pin_scan = 22
button_pin_power = 5
button_pin_go = 27
button_pin_horn = 17
bbutton_pin_manual = 4

led_pin_power = 18
led_pin_scanning = 23
led_pin_found_qr = 24

# initialise a previous input variable to 0 (assume button not pressed last)
qr_found = False
time_stamp = time.time()
debounce = 0.3

# Prepare Pi Camera Module
try:
    camera = photo.prepare_camera()
except:
    print("Camera Not Ready")

# instantiate CommLink
comm_link = CommLink(port="/dev/ttyACM0", baud_rate=9600)

# Button States
powered_off = False
scanning = False
going = False
horn = False
manual = False
command_string = ""

# handle the button event


def PowerPressed(pin):
    global time_stamp       # put in to debounce
    global debounce
    global powered_off
    global scanning
    global going
    time_now = time.time()
    if (time_now - time_stamp) >= debounce and powered_off == False and scanning == False and going == False:
        powered_off = True
        print("Power Button pressed")
        # Turn power LED OFF
        GPIO.output(led_pin_power, False)
        # Issue a poweroff command
        os.system("poweroff")
    time_stamp = time_now

# handle the button event


def ScanPressed(pin):
    global time_stamp       # put in to debounce
    global debounce
    global powered_off
    global scanning
    global going
    global camera
    global led_pin_scanning
    global led_pin_found_qr
    global qr_found
    global command_string

    time_now = time.time()
    if (time_now - time_stamp) >= debounce and powered_off == False and scanning == False and going == False:
        # Play a sound to show that we are scanning
        audio.playSound(0)
        # Flag that we are scanning
        scanning = True
        print("Scan Button pressed")
        # Call python script to try and find QR code from webcam image
        GPIO.output(led_pin_scanning, True)  # Turn on the "scanning" LED
        GPIO.output(led_pin_found_qr, False)  # Ensure Found QR LED OFF

        # Try to find a QR code from the camera.
        QRCode = qrscanner.FindQRCode(led_pin_scanning, camera, 10)
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
        scanning = False
    time_stamp = time_now


# handle the button event
def GoPressed(pin):
    global time_stamp       # put in to debounce
    global debounce
    global powered_off
    global scanning
    global going
    global command_string

    time_now = time.time()
    if (time_now - time_stamp) >= debounce and powered_off == False and scanning == False and going == False:
        going = True
        print("Go Button pressed")
        if (qr_found == True and command_string != ""):
            # Play a sound to show that we are scanning
            audio.playSound(10)  # play start sound

            arduino_comms.parsecommand_string(command_string)

            # Play sound that we found one
            audio.playSound(10)

            # Success GO operation, turn LED off and flag QR found as FALSE for
            # next go
            GPIO.output(led_pin_found_qr, False)
            qr_found = False
            # Pass command to motor controller here
        else:
            print("No QR Found, scan again please")
        going = False
    time_stamp = time_now


def hornPressed(pin):
    global time_stamp       # put in to debounce
    global debounce
    global powered_off
    global scanning
    global going
    global horn
    time_now = time.time()
    if (time_now - time_stamp) >= debounce and powered_off == False and scanning == False and horn == False:
        horn = True
        print("horn Pressed")
        audio.playSound(11)
        horn = False
    time_stamp = time_now


def manualPressed(pin):
    global time_stamp       # put in to debounce
    global debounce
    global powered_off
    global scanning
    global going
    global horn
    global manual
    time_now = time.time()
    if (time_now - time_stamp) >= debounce and powered_off == False and scanning == False and horn == False and manual == False:
        manual = True
        print("manual Pressed")
        audio.playSound(11)
        manual = False
    time_stamp = time_now


def WaitForButton():
    # Advise user what to do
    print "Press button to start scanning"

    try:
        # Set GPIO mode and pre-config gpio ports as either IN or OUT
        GPIO.setmode(GPIO.BCM)
        # print "DEBUG-SetMode"

        # Setup GPIO port for Buttons, ready for interrupt
        GPIO.setup(button_pin_power, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(button_pin_scan, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(button_pin_go, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(button_pin_horn, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(bbutton_pin_manual, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        # Add callbacks for all EXCEPT the power button.
        GPIO.add_event_detect(
            button_pin_scan, GPIO.RISING, callback=ScanPressed)
        GPIO.add_event_detect(button_pin_go, GPIO.RISING, callback=GoPressed)
        GPIO.add_event_detect(
            button_pin_horn, GPIO.RISING, callback=hornPressed)
        GPIO.add_event_detect(
            bbutton_pin_manual, GPIO.RISING, callback=manualPressed)
        # print "DEBUG-Setup and Add_Events"

        # Setup GPIO ports for LEDs
        GPIO.setup(led_pin_power, GPIO.OUT)
        GPIO.setup(led_pin_found_qr, GPIO.OUT)
        GPIO.setup(led_pin_scanning, GPIO.OUT)
        GPIO.output(led_pin_power, True)  # Turn Power LED ON
        GPIO.output(led_pin_found_qr, False)  # Ensure Found QR LED OFF
        GPIO.output(led_pin_scanning, False)  # Ensure scanning LED OFF
        # print "DEBUG-Setup and Output LEDs"

        # Main wait is for the power button, all other GPIOs are callbacks
        GPIO.wait_for_edge(button_pin_power, GPIO.FALLING)
        PowerPressed(button_pin_power)

    except:
        print("Exception Caught")
        GPIO.cleanup()       # clean up GPIO on CTRL+C exit

    # Clean up GPIO settings
    GPIO.cleanup()


# Main()
WaitForButton()
