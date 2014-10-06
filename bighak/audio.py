import subprocess


def get_sound_url(sound_id):
    basePath = "/home/pi/qrscanner/audio/"
    if 0 <= sound_id <= 3:
        return basePath+"key-0-3.wav"
    elif 4 <= sound_id <= 6:
        return basePath+"key-4-6.wav"
    elif 7 <= sound_id <= 9:
        return basePath+"key-7-9.wav"
    elif sound_id == 10:
        return basePath+"start.wav"
    elif sound_id == 11:
        return basePath+"pew.wav"
    elif sound_id == 12:
        return basePath+"key-command.wav"
    else:
        return basePath+"high-key.wav"


def playSound(sound_id):
    cmd = "aplay -q "+get_sound_url(sound_id)
    process = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
    (out, err) = process.communicate()
