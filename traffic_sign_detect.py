import cv2
import numpy as np
from classification import getLabel, load_model, training
from cameracapture import Camera
from threading import Thread, Lock
import time

SIGNS = ["ERROR",
        "STOP",
        "TURN LEFT",
        "TURN RIGHT",
        "OTHER"]

class TrafficSignDetection():
    def __init__(self, show=False) -> None:
        self.model = load_model()
        self.last_label = None
        self.error = 0
        self.show = show
        self.status_image = None
        self.thread_lock = Lock()

        self.is_running = False 
        self.start()

    def _cropSign(self, image, coordinate):
        width = image.shape[1]
        height = image.shape[0]
        top = max([int(coordinate[0][1]), 0])
        bottom = min([int(coordinate[1][1]), height-1])
        left = max([int(coordinate[0][0]), 0])
        right = min([int(coordinate[1][0]), width-1])
        return image[top:bottom,left:right]
    def trafficsigndetect(self):
        camera = Camera()
        try:
            while self.is_running:
                try :
                    with camera.thread_lock:
                        time.sleep(0.1)
                        success, image = camera.read()
                        if not success or image is None :
                            continue
                        image = cv2.resize(image, (640, 480))

                        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
                        edges = cv2.Canny(blurred, 50, 150)
                        if self.show:
                            cv2.imshow('blur', blurred)
                            cv2.imshow('gray', gray)
                            cv2.imshow('edges', edges)
                        # Use Hough Circle Transform for circle detection
                        circles = cv2.HoughCircles(
                            edges, cv2.HOUGH_GRADIENT, dp=1, minDist=50, param1=70, param2=50, minRadius=10, maxRadius=200
                        )

                        # Draw detected circles
                        if circles is not None:
                            circles = np.uint16(np.around(circles))
                            max_circle = None 
                            
                            for i in circles[0,:]:
                                coordinate = [(i[0] - i[2], i[1] - i[2]), (i[0] + i[2], i[1] + i[2])]
                                circle_region = self._cropSign(image, coordinate) 
                                
                                avg_color = np.mean(circle_region, axis=(0, 1))
                                # Check if the color is predominantly red or blue
                                if avg_color[2] > avg_color[0] and avg_color[2] > avg_color[1] or avg_color[0] > avg_color[1] and avg_color[0] > avg_color[2]:  # Blue  or Red
                                    if max_circle is None:
                                        max_circle = i
                                    else:
                                        if i[2] > max_circle[2]:
                                            max_circle = i
                            
                            if max_circle is None:
                                continue
                            coordinate = ((max_circle[0] - max_circle[2], max_circle[1] - max_circle[2]), (max_circle[0] + max_circle[2], max_circle[1] + max_circle[2]))

                            sign = self._cropSign(image, coordinate)
                            if self.show:
                                cv2.imshow("output.png", sign)
                            cv2.circle(image, (max_circle[0], max_circle[1]), max_circle[2], (0, 255, 0), 2)  # Draw the outer circle
                            cv2.circle(image, (max_circle[0], max_circle[1]), 2, (0, 0, 255), 3)  # Draw the center of the circle

                            label = getLabel(self.model, sign)
                            font = cv2.FONT_HERSHEY_PLAIN

                            if label != 0:
                                self.last_label = label
                                print(SIGNS[label], max_circle[0] - 320)

                            if self.last_label is not None:
                                font = cv2.FONT_HERSHEY_PLAIN
                                cv2.putText(image,SIGNS[label],(coordinate[0][0], coordinate[0][1] -15), font, 1,(0,0,255),2,cv2.LINE_4)
                        # Display the result
                        self.status_image = image
                        if self.show:
                            cv2.imshow('Detected Circles', image)
                            if cv2.waitKey(1) & 0xFF == ord('q'):
                                break
                except Exception as e:
                    print(e)
                    pass
        except Exception as e:
            print(e)
            return
        finally:
            if self.show:
                cv2.destroyAllWindows()
            camera.stop()
    def read(self):
        return self.last_label, self.error
    def getImage(self):
        return self.status_image

    def start(self):
        self.is_running = True
        thread = Thread(target=self.trafficsigndetect)
        thread.start()

    def stop(self):
        self.is_running = False

if __name__ == "__main__":
    detect = TrafficSignDetection(show=True)

