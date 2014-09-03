import RPi.GPIO as GPIO
import time
import qrscanner
import photo
import os
import audio
import parseQR
import arduinoComms

# GPIO Pin numbers
buttonPinScan = 22
buttonPinPower = 5
buttonPinGo = 27
buttonPinHorn = 17
buttonPinManual = 4

ledPinPower = 18
ledPinScanning = 23
ledPinFoundQR = 24

#initialise a previous input variable to 0 (assume button not pressed last)
bFoundQR = False
time_stamp = time.time()
debounce = 0.3

# Prepare Pi Camrea Module
try:
    camera = photo.PrepareCamera()
except:
    print("Camera Not Ready")

# Button States
PoweredOff = False
Scanning = False
Going = False
Horn = False
Manual = False
commandString = ""

# handle the button event
def PowerPressed(pin):
    global time_stamp       # put in to debounce
    global debounce
    global PoweredOff
    global Scanning
    global Going
    time_now = time.time()
    if (time_now - time_stamp) >= debounce and PoweredOff==False and Scanning==False and Going==False:
        PoweredOff = True
        print("Power Button pressed")
        # Turn power LED OFF
        GPIO.output(ledPinPower, False)
        # Issue a poweroff command
        os.system( "poweroff" )
    time_stamp = time_now

# handle the button event
def ScanPressed(pin):
    global time_stamp       # put in to debounce
    global debounce
    global PoweredOff
    global Scanning
    global Going
    global camera
    global ledPinScanning
    global ledPinFoundQR
    global bFoundQR
    global commandString

    time_now = time.time()
    if (time_now - time_stamp) >= debounce and PoweredOff==False and Scanning==False and Going==False:
        # Play a sound to show that we are scanning
        audio.playSound(0)
        # Flag that we are scanning
        Scanning = True
        print("Scan Button pressed")
        # Call python script to try and find QR code from webcam image
        GPIO.output(ledPinScanning, True) # Turn on the "Scanning" LED
        GPIO.output(ledPinFoundQR, False) # Ensure Found QR LED OFF

        # Try to find a QR code from the camera.
        QRCode = qrscanner.FindQRCode(ledPinScanning, camera, 10)
        if (QRCode != ""):
            # Play sound that we found one
            audio.playSound(10)

            # Found a QR Code, Strip out the command portion of the string
            commandString = parseQR.parseOutCommand(QRCode)
            # Flag that we found a QR code
            bFoundQR = True
            # Ensure Found QR LED OFF
            GPIO.output(ledPinFoundQR, True)

        # Turn off the "Scanning" LED
        GPIO.output(ledPinScanning, False)
        Scanning = False
    time_stamp = time_now


# handle the button event
def GoPressed(pin):
    global time_stamp       # put in to debounce
    global debounce
    global PoweredOff
    global Scanning
    global Going
    global commandString

    time_now = time.time()
    if (time_now - time_stamp) >= debounce and PoweredOff==False and Scanning==False and Going==False:
        Going = True
        print("Go Button pressed")
        if (bFoundQR == True and commandString != ""):
            # Play a sound to show that we are scanning
            audio.playSound(10) # play start sound

            arduinoComms.parseCommandString(commandString)

            # Play sound that we found one
            audio.playSound(10)

            # Success GO operation, turn LED off and flag QR found as FALSE for next go
            GPIO.output(ledPinFoundQR, False)
            bFoundQR = False
            # Pass command to motor controller here
        else:
            print("No QR Found, scan again please")
        Going = False
    time_stamp = time_now


def HornPressed(pin):
    global time_stamp       # put in to debounce
    global debounce
    global PoweredOff
    global Scanning
    global Going
    global Horn
    time_now = time.time()
    if (time_now - time_stamp) >= debounce and PoweredOff==False and Scanning==False and Horn==False:
        Horn = True
        print("Horn Pressed")
        audio.playSound(11)
        Horn = False
    time_stamp = time_now
    

def ManualPressed(pin):
    global time_stamp       # put in to debounce
    global debounce
    global PoweredOff
    global Scanning
    global Going
    global Horn
    global Manual
    time_now = time.time()
    if (time_now - time_stamp) >= debounce and PoweredOff==False and Scanning==False and Horn==False and Manual==False:
        Manual = True
        print("Manual Pressed")
        audio.playSound(11)
        Manual = False
    time_stamp = time_now
    

def WaitForButton():
    # Advise user what to do
    print "Press button to start scanning"
    
    try:
        # Set GPIO mode and pre-config gpio ports as either IN or OUT
        GPIO.setmode(GPIO.BCM)
        #print "DEBUG-SetMode"
        
        # Setup GPIO port for Buttons, ready for interrupt
        GPIO.setup(buttonPinPower, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(buttonPinScan, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(buttonPinGo, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(buttonPinHorn, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(buttonPinManual, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        # Add callbacks for all EXCEPT the power button.
        GPIO.add_event_detect(buttonPinScan, GPIO.RISING, callback=ScanPressed)
        GPIO.add_event_detect(buttonPinGo, GPIO.RISING, callback=GoPressed)
        GPIO.add_event_detect(buttonPinHorn, GPIO.RISING, callback=HornPressed)
        GPIO.add_event_detect(buttonPinManual, GPIO.RISING, callback=ManualPressed)
        #print "DEBUG-Setup and Add_Events"
        
        # Setup GPIO ports for LEDs
        GPIO.setup(ledPinPower, GPIO.OUT)
        GPIO.setup(ledPinFoundQR, GPIO.OUT)
        GPIO.setup(ledPinScanning, GPIO.OUT)
        GPIO.output(ledPinPower, True) # Turn Power LED ON
        GPIO.output(ledPinFoundQR, False) # Ensure Found QR LED OFF
        GPIO.output(ledPinScanning, False) # Ensure Scanning LED OFF
        #print "DEBUG-Setup and Output LEDs"
              
        # Main wait is for the power button, all other GPIOs are callbacks
        GPIO.wait_for_edge(buttonPinPower, GPIO.FALLING)
        PowerPressed(buttonPinPower)
    
    except:
        print("Exception Caught")
        GPIO.cleanup()       # clean up GPIO on CTRL+C exit
    
    # Clean up GPIO settings
    GPIO.cleanup()


# Main()
WaitForButton()
