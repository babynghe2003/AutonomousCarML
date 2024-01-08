import cv2
import time
from flask import Flask, render_template, Response, stream_with_context, request
from traffic_sign_detect import TrafficSignDetection
from l298n import Motor 
from threading import Thread

app = Flask('__name__')
detector = TrafficSignDetection(show=False)
motor = Motor()

def video_stream():
    time.sleep(0.1)
    while True:
        with detector.thread_lock:
            image = detector.getImage()
            if image is None:
                continue
            cv2.imwrite("frame.jpg", image)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + open('frame.jpg', 'rb').read() + b'\r\n')
            key = cv2.waitKey(1) & 0xFF
            time.sleep(0.1)
            if key == ord('q'):
                break

def car_control():
    time.sleep(5)
    while True:
        with detector.thread_lock:
            label, error = detector.read()
            print(label, error)
            motor.setMotor(30-error/10, 30+error/10)

@app.route('/')
def index():
    return render_template('camera.html')

@app.route('/video_feed')
def video_feed():
    return Response(video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    car_thread = Thread(target=car_control)
    car_thread.start()
    app.run(debug=True, threaded=True, port=5000)
