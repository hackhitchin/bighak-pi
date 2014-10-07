import sys
import arduino_comms
import parseQR
import qrscanner
import photo
import audio

# Prepare Pi Camrea Module
try:
    camera = photo.prepare_camera()
except:
    print("Camera Not Ready")

comm_link = arduino_comms.CommLink(port="/dev/ttyACM0", baud_rate=9600)

ledPinScanning = 23

QRCode = qrscanner.FindQRCode(ledPinScanning, camera, 10)
if (QRCode != ""):
    # Show us the Command String
    print(QRCode)
    # Found a QR Code, Strip out the command portion of the string
    commandString = parseQR.parseOutCommand(QRCode)

    # Play start sound
    audio.play_sound(10)

    # Send command to arduino
    # print(commandString)
    comm_link.parse_command_string(commandString)

    # Play stop sound
    audio.play_sound(10)
else:
    print("Not Found")
