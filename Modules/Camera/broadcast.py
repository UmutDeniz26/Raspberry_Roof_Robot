import subprocess

# Command to receive the video stream using ffmpeg
command = [
    'ffmpeg',
    '-i', 'udp://192.168.1.13:1234',
    '-f', 'image2pipe',
    '-pix_fmt', 'bgr24',
    '-vcodec', 'rawvideo', '-'
]

# Start ffmpeg process
ffmpeg_process = subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=10**8)

while True:
    # Read frame from ffmpeg process
    raw_image = ffmpeg_process.stdout.read(640 * 480 * 3)  # Assuming video size is 640x480
    if len(raw_image) != 640 * 480 * 3:
        break

    # Process the raw image (you can use OpenCV for this)
    # Example:
    # import cv2
    # frame = cv2.imdecode(numpy.frombuffer(raw_image, dtype=numpy.uint8), cv2.IMREAD_COLOR)
    # cv2.imshow('Video', frame)
    # cv2.waitKey(1)

# Clean up
ffmpeg_process.kill()
