from picamera2 import Picamera2
import os 


def take_picture_and_save(camera, save_file = None ):
    if save_file is None:
        save_file = os.path.join(os.getcwd(), os.path.join(os.path.dirname(__file__), "output/test.jpg"))
    if not isinstance(camera, Picamera2):
        raise ValueError("Camera must be an instance of Picamera2")
    camera.start_and_capture_file(save_file)

def record_video_and_save(camera, save_file = None, duration = 5):
    if save_file is None:
        #Craete FileOutput object
        save_file = os.path.join(os.getcwd(), os.path.join(os.path.dirname(__file__), "output/test.h264"))
    print("Start recording")
    camera.start_and_record_video(output=save_file, duration=duration, show_preview=True)
    print("Recording finished and saved to ", save_file)

picam2 = Picamera2()
picam2.vflip = True
take_picture_and_save(picam2)
#record_video_and_save(picam2)
