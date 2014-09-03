#import pyaudio  
#import wave  
import subprocess

def getSoundURL(n):
    basePath = "/home/pi/qrscanner/audio/"
    if n == 0 or n == 1 or n == 2 or n == 3:
        return basePath+"key-0-3.wav"
    elif n == 4 or n == 5 or n == 6:
        return basePath+"key-4-6.wav"
    elif n == 7 or n == 8 or n == 9:
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
