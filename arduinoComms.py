import serial # pyserial
from time import sleep
import audio
from datetime import datetime

def repeatSend(serial, command_verb, nSeconds, INTERVAL):
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
        serial.write('Z' * LASER_REPEATS)
        # Play sound
        audio.playSound(11)
        # Lower case 'z' to turn LED OFF
        serial.write('z' * LASER_REPEATS)
        print('z' * LASER_REPEATS)
        sleep(0.3)
    else:
        while (nSeconds > 0.0):
            print(command_verb)
            serial.write(command_verb)
            sleep(INTERVAL)
            nSeconds = nSeconds - INTERVAL

def send_command_string(serial, command_verb, command_value):
    
    # uppercase the command_verb
    command_verb = command_verb.upper()

    # Simply write to the serial device
    INTERVAL = 0.5 # In Seconds
    FB_SECONDS = 1.0
    LR_SECONDS = 0.125
    P_SECONDS = 0.5
    loop = 0
    while (loop < command_value):
        if (command_verb.upper() in ['F','B']:
            repeatSend(serial, command_verb, FB_SECONDS, INTERVAL)
        if (command_verb.upper() in['L', 'R']):
            repeatSend(serial, command_verb, LR_SECONDS, INTERVAL)
        if (command_verb.upper() in ['P', 'Z']):
            repeatSend(serial, command_verb, P_SECONDS, INTERVAL)
        loop = loop + 1

def parseCommandString(command_string):

    # Open the serial communication port
    ser = serial.Serial('/dev/ttyACM0', 9600)

    nPause = 0.5
    nIndex = 0
    command_verb = ' '
    command_value = 0
    countString = '' # Initialise count string
    chunk_length = 3 # our commands are always 3 char where [0] is verb, [1][2] is the value (left padded)

    command_list = [command_string[i:i+step] for i in range(0, len(command_string), chunk_length)]

    for c in command_string:
        if not c.isdigit():
            if command_verb != ' ':
                sleep(nPause)
                command_value = int(countString)
                send_command_string(ser, command_verb, command_value)
            # 'c' should be the command verb (but not guaranteed, its only NOT A NUMBER)
            command_verb = c

            # New command char found, reset count info
            countString = ''
            command_value = 0
        else:
            # Add int char to int string
            countString += c

        # If its the final char, send it
        if nIndex == len(commandString)-1 and command_verb != ' ':
            sleep(nPause)
            command_value = int(countString)
            send_command_string(ser, command_verb, command_value)

        # Increment loop counter
        nIndex = nIndex+1


# Main
if __name__== "__main__":
    command_string = raw_input("enter command string:")
    parseCommandString(command_string)
