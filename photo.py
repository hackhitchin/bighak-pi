import picamera

def prepare_camera():
    # Prepare camera for image capture
    camera = picamera.PiCamera();
    return camera;

def take_photo(camera, szFilename):
    # Capture a single image
    camera.capture(szFilename);
    return;
