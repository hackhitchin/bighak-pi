import arduinoComms
import parseQR
import qrscanner
import sys
import photo
import audio

#data = sys.stdin.readlines()
#searchString = '\"command\":\"'
#commandIndex = data.find(searchString)
#commandString = ""
#commandIndex = tempString.find('\",')
#if (commandIndex != -1):#
#	commandString = tempString[0:commandIndex]

# Prepare Pi Camrea Module
try:
    camera = photo.PrepareCamera()
except:
    print("Camera Not Ready")

ledPinScanning = 23

QRCode = qrscanner.FindQRCode(ledPinScanning, camera, 10)
if (QRCode != ""):
    # Show us the Command String
    print(QRCode)
    # Found a QR Code, Strip out the command portion of the string
    commandString = parseQR.parseOutCommand(QRCode)

    # Play start sound
    audio.playSound(10)

    # Send command to arduino
    #print(commandString)
    arduinoComms.parseCommandString(commandString)

    # Play stop sound
    audio.playSound(10)
else:
    print("Not Found")

