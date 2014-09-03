#from cv2.cv import *
## Initialize the camera
#capture = CaptureFromCAM(0)  # 0 -> index of camera
#if capture:     # Camera initialized without any errors
#   f = QueryFrame(capture)     # capture the frame
#   if f:
#       SaveImage("/mnt/ramdisk/test.jpg", f)#
import picamera

def PrepareCamera():
    # Prepare camera for image capture
    camera = picamera.PiCamera();
    return camera;

def TakePhoto(camera, szFilename):
    # Capture a single image
    camera.capture(szFilename);
    return;
