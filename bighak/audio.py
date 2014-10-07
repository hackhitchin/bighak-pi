import os
import subprocess


def get_sound_url(sound_id):
    #TODO - remove hard coding here and make relative to module path
    base_path = "/home/pi/qrscanner/bighak/audio/"
    filename = "high-key.wav"
    if 0 <= sound_id <= 3:
        filename = "key-0-3.wav"
    elif 4 <= sound_id <= 6:
        filename = "key-4-6.wav"
    elif 7 <= sound_id <= 9:
        filename = "key-7-9.wav"
    elif sound_id == 10:
        filename = "start.wav"
    elif sound_id == 11:
        filename = "pew.wav"
    elif sound_id == 12:
        filename = "key-command.wav"

    return os.path.join(base_path, filename)


def play_sound(sound_id):
    cmd = "aplay -q "+get_sound_url(sound_id)
    process = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
    (out, err) = process.communicate()
