from picamera2 import Picamera2
import os 

def take_picture_and_save(camera, save_file = None ):
    if save_file is None:
        save_file = os.path.join(os.getcwd(), os.path.join(os.path.dirname(__file__), "test.jpg"))
    if not isinstance(camera, Picamera2):
        raise ValueError("Camera must be an instance of Picamera2")
    camera.start_and_capture_file(save_file)

picam2 = Picamera2()
take_picture_and_save(picam2)

