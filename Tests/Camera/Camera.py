from picamera2 import Picamera2, Preview
from picamera2.outputs import FfmpegOutput, FileOutput
from picamera2.encoders import H264Encoder
import os 
import time


def take_picture_and_save(camera, save_file = None ):
    if save_file is None:
        save_file = os.path.join(os.getcwd(), os.path.join(os.path.dirname(__file__), "output/test.jpg"))
    if not isinstance(camera, Picamera2):
        raise ValueError("Camera must be an instance of Picamera2")
    camera.start_and_capture_file(save_file)

def record_video_and_save(camera, save_file = None, duration = 5):
    """
    :param camera: Picamera2 object
    :param save_file: FileOutput object
    """

    if save_file is None:
        #Craete FileOutput object
        save_file = os.path.join(os.getcwd(), os.path.join(os.path.dirname(__file__), "output/test.h264"))
    print("Start recording")
    camera.start_and_record_video(output=save_file, duration=duration, show_preview=True)
    print("Recording finished and saved to ", save_file)
import subprocess

def convert_h264_to_mp4(h264_file, mp4_file):
    if not os.path.exists(h264_file):
        raise FileNotFoundError("File not found")
    if not h264_file.endswith(".h264"):
        raise ValueError("Input file must be a h264 file")
    if not mp4_file.endswith(".mp4"):
        raise ValueError("Output file must be a mp4 file")
    if os.path.exists(mp4_file):
        os.remove(mp4_file)
    
    # Conversion command using ffmpeg
    command = ["ffmpeg", "-i", h264_file, "-c:v", "copy", "-c:a", "aac", mp4_file]
    # Execute the command
    try:
        subprocess.run(command, check=True)
        print("Conversion successful!")
    except subprocess.CalledProcessError as e:
        print("Error during conversion:", e)


def test(picam2):
    camera_config = picam2.create_preview_configuration()
    picam2.configure(camera_config)
    picam2.start_preview(Preview.QTGL)
    picam2.start()
    time.sleep(2)
    save_file = os.path.join(os.getcwd(), os.path.join(os.path.dirname(__file__), "output/test.jpg"))
    picam2.capture_file(save_file)

picam2 = Picamera2()
picam2.vflip = True
#take_picture_and_save(picam2)
record_video_and_save(picam2)
save_file = os.path.join(os.getcwd(), os.path.join(os.path.dirname(__file__), "output/test.h264"))
convert_h264_to_mp4(save_file, save_file.replace(".h264", ".mp4"))
#test(picam2)

