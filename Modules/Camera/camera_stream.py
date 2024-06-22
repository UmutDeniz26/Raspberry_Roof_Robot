from flask import Flask, Response
from picamera2 import Picamera2
import cv2

### You can donate at https://www.buymeacoffee.com/mmshilleh 

def camera_stream_start(port=5000):

    app = Flask(__name__)
    
    camera = Picamera2()
    # Verbose should be False to avoid printing the camera configuration
    camera.verbose = False
    camera.configure(camera.create_preview_configuration(main={"format": 'XRGB8888', "size": (800, 606)}) )
    camera.start()

    @app.route('/video_feed')
    def video_feed():
        return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def generate_frames():
        while True:
            frame = camera.capture_array()
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    app.run(host='0.0.0.0', port = port)

if __name__ == '__main__':
    camera_stream_start( 8080 )