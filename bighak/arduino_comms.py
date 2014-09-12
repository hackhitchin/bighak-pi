import serial
from time import sleep
import audio
from datetime import datetime


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
            (['F','B'], FB_SECONDS),
            (['L','R'], LR_SECONDS),
            (['P','Z'], PZ_SECONDS),
        ]

        # generate a list of the 2nd tuple items where the command_verb is present in the first tuple item
        match_list = [item[1] for item in interval_map if command_verb.upper() in item[0]]
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
            sleep(0.3)
        else:
            while (nSeconds > 0.0):
                print(command_verb)
                self.serial_link.write(command_verb)
                sleep(INTERVAL)
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

        command_list = [command_string[i:i+chunk_length] for i in
                        range(0, len(command_string), chunk_length)]

        for command in command_list:
            # decompose command into command_verb & command_value
            command_verb, command_value = command[:1], command[1:]

            # if for some reason we have an incomplete command, 
            # command value will be a zero length string
            # in that case, skip it
            if command_value != "":
                # pause
                sleep(pause_length)
                #send the command (cast command value to int first)
                self.send_command_string(command_verb, int(command_value)


# Main
if __name__== "__main__":
    comm_link = CommLink(port="/dev/ttyACM0", baud_rate=9600)
    command_string = raw_input("enter command string:")
    comm_link.parse_command_string(command_string)
