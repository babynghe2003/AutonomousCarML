import cv2
import numpy as np
import time

def cropSign(image, coordinate):
    width = image.shape[1]
    height = image.shape[0]
    top = max([int(coordinate[0][1]), 0])
    bottom = min([int(coordinate[1][1]), height-1])
    left = max([int(coordinate[0][0]), 0])
    right = min([int(coordinate[1][0]), width-1])
    return image[top:bottom,left:right]
vidcap = cv2.VideoCapture(0)

last_label = None
file_index = 169 
while True:
    try:
        success, image = vidcap.read()
        image = cv2.resize(image, (640, 480))

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        cv2.imshow('edges', edges)

        # Use Hough Circle Transform for circle detection
        circles = cv2.HoughCircles(
            edges, cv2.HOUGH_GRADIENT, dp=1, minDist=50, param1=60, param2=50, minRadius=10, maxRadius=200
        )

        # Draw detected circles
        if circles is not None:
            circles = np.uint16(np.around(circles))
            max_circle = None 

            for i in circles[0,:]:
                coordinate = [(i[0] - i[2], i[1] - i[2]), (i[0] + i[2], i[1] + i[2])]
                circle_region = cropSign(image, coordinate) 
                
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

            sign = cropSign(image, coordinate)
            sign = cv2.resize(sign,(32,32))
            cv2.imshow("output.png", sign)
            cv2.imwrite("./dataset/1/({}).png".format(file_index), sign)
            cv2.imshow('result', sign)
            file_index+=1
            
        # Display the result
        cv2.imshow('Detected Circles', image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    except Exception as e:
        pass
    finally:
        time.sleep(0.5)
        print(file_index)
cv2.destroyAllWindows()
