import serial # pyserial
from time import sleep
import audio
from datetime import datetime

def isNumber(c):
    # Simple test for whether character is a number
    if (c=='0' or c=='1' or c=='2' or c=='3' or c=='4' or c=='5' or c=='6' or c=='7' or c=='8' or c=='9'):
        return True
    return False

def repeatSend(serial, commandChar, nSeconds, nInterval):
    # Send a single char repeatedly at a specific
    # interval for a specific length of time.
    # Have to play fireing sound here as it sounds as it lights LED
    if (commandChar == 'P'):
        # Play a sound to show that we are scanning
        audio.playSound(11)

    if (commandChar == 'Z'):
        # Uppercase 'Z' to turn LED ON
        print(commandChar)
        print(commandChar)
        print(commandChar)
        print(commandChar)
        print(commandChar)
        serial.write('Z')
        serial.write('Z')
        serial.write('Z')
        serial.write('Z')
        serial.write('Z')
        # Play sound
        audio.playSound(11)
        # Lowert case 'z' to turn LED OFF
        serial.write('z')
        serial.write('z')
        serial.write('z')
        serial.write('z')
        serial.write('z')
        print('z')
        print('z')
        print('z')
        print('z')
        print('z')
        sleep(0.3)
    else:
        while (nSeconds > 0.0):
            print(commandChar)
            serial.write(commandChar)
            sleep(nInterval)
            nSeconds = nSeconds - nInterval

def sendCommandString(serial, commandChar, count):
    # Simply write to the serial device
    nInterval = 0.5 # In Seconds
    nFBSeconds = 1.0
    nLRSeconds = 0.125
    nPSeconds = 0.5
    loop = 0
    while (loop < count):
        #print(str(loop))
        if (commandChar == 'F' or commandChar == 'B'):
            repeatSend(serial, commandChar, nFBSeconds, nInterval)
        if (commandChar == 'L' or commandChar == 'R'):
            repeatSend(serial, commandChar, nLRSeconds, nInterval)
        if (commandChar == 'P' or commandChar == 'Z'):
            repeatSend(serial, commandChar, nPSeconds, nInterval)
        loop = loop + 1

def parseCommandString(commandString):
    # Open the serial communication port
    ser = serial.Serial('/dev/ttyACM0', 9600)

    nPause = 0.5
    nIndex = 0
    commandChar = ' '
    commandCount = 0
    countString = '' # Initialise count string
    for c in commandString:
        if ( isNumber(c) == False ):
            if (commandChar != ' '):
                #print(" ")
                sleep(nPause)
                commandCount = int(countString)
                sendCommandString(ser, commandChar, commandCount)
            # 'c' should be the command character (but not garanteed, its only NOT A NUMBER)
            commandChar = c

            # New command char found, reset count info
            countString = ''
            commandCount = 0
        else:
            # Add int char to int string
            countString += c

        # If its the final char, send it
        if (nIndex == len(commandString)-1 and commandChar != ' '):
            #print(" ")
            sleep(nPause)
            commandCount = int(countString)
            sendCommandString(ser, commandChar, commandCount)

        # Increment loop counter
        nIndex = nIndex+1


# Main
if __name__== "__main__":
    command_string = raw_input("enter command string:")
    parseCommandString(command_string)
