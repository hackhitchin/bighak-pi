#import pyaudio  
#import wave  
import subprocess

def getSoundURL(n):
    basePath = "/home/pi/qrscanner/audio/"
    if 0 <= n <= 3:
        return basePath+"key-0-3.wav"
    elif 4 <= n <= 6:
        return basePath+"key-4-6.wav"
    elif 7 <= n <= 9:
        return basePath+"key-7-9.wav"
    elif n == 10:
        return basePath+"start.wav"
    elif n == 11:
        return basePath+"pew.wav"
    elif n == 12:
        return basePath+"key-command.wav"
    else:
        return basePath+"high-key.wav"

def playSound(nSound):
    process = subprocess.Popen(["aplay -q "+getSoundURL(nSound)], stdout=subprocess.PIPE, shell=True)
    (out, err) = process.communicate()


# main
#playSound(10)
