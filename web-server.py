import cv2
import numpy as np
from classification import getLabel, training, load_model
from picamera.array import PiRGBArray
from picamera import PiCamera
from l298n import Motor 
import time
from flask import Flask, render_template, Response, stream_with_context, request

SIGNS = ["ERROR",
        "STOP",
        "TURN LEFT",
        "TURN RIGHT",
        "OTHER"]

def cropSign(image, coordinate):
    width = image.shape[1]
    height = image.shape[0]
    top = max([int(coordinate[0][1]), 0])
    bottom = min([int(coordinate[1][1]), height-1])
    left = max([int(coordinate[0][0]), 0])
    right = min([int(coordinate[1][0]), width-1])
    return image[top:bottom,left:right]

model = load_model()
last_label = None

motor = Motor()

ki = 0.00005
kd = 0.01
kp = 0.1

P = 0
I = 0
D = 0

last_error = 0
last_time = time.time()

def pid(error):
    global P, I, D, last_error, last_time
    P = error
    I += error
    D = (error - last_error) / (time.time() - last_time)
    last_error = error
    last_time = time.time()
    return P * kp + I * ki + D * kd

camera = PiCamera()
camera.resolution = (640,480)
camera.framerate = 40
rawCapture = PiRGBArray(camera, size=(640,480))

time.sleep(1)
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    try:
        # success, image = vidcap.read()
        image = frame.array
        image = cv2.resize(image, (640,480))
        width = image.shape[1]
        height = image.shape[0]

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        
        cv2.imshow("edges", edges)

        # Use Hough Circle Transform for circle detection
        circles = cv2.HoughCircles(
            edges, cv2.HOUGH_GRADIENT, dp=1, minDist=50, param1=80, param2=70, minRadius=4, maxRadius=220
        )

        # Draw detected circles
        if circles is not None:
            circles = np.uint16(np.around(circles))
            max_circle = None 
            
            for i in circles[0,:]:
                if max_circle is None:
                    max_circle = i
                else:
                    if i[2] > max_circle[2]:
                        max_circle = i
            
            if max_circle is None:
                continue

            coordinate = ((max_circle[0] - max_circle[2], max_circle[1] - max_circle[2]), (max_circle[0] + max_circle[2], max_circle[1] + max_circle[2]))

            sign = cropSign(image, coordinate)

            cv2.circle(image, (max_circle[0], max_circle[1]), max_circle[2], (0, 255, 0), 2)  # Draw the outer circle
            cv2.circle(image, (max_circle[0], max_circle[1]), 2, (0, 0, 255), 3)  # Draw the center of the circle

            label = getLabel(model, sign)
            font = cv2.FONT_HERSHEY_PLAIN

            if label != 0 and label != last_label:
                last_label = label

            if label != 0:
                diff_speed = pid(width/2 - max_circle[0])
                print(diff_speed)
#                 motor.forward(35 + diff_speed, 35 - diff_speed)

            print(SIGNS[label])
            font = cv2.FONT_HERSHEY_PLAIN
            cv2.putText(image,SIGNS[label],(coordinate[0][0], coordinate[0][1] -15), font, 1,(0,0,255),2,cv2.LINE_4)
        # Display the result
        cv2.imshow('Detected Circles', image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    except Exception as e:
        pass
    finally:
        rawCapture.truncate(0)
camera.close()
cv2.destroyAllWindows()
motor.stop()
