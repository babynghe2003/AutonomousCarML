import cv2
import numpy as np
from classification import getLabel, load_model, training


SIGNS = ["ERROR",
        "STOP",
        "TURN LEFT",
        "TURN RIGHT",
        "OTHER"]

vidcap = cv2.VideoCapture(0)

def cropSign(image, coordinate):
    width = image.shape[1]
    height = image.shape[0]
    top = max([int(coordinate[0][1]), 0])
    bottom = min([int(coordinate[1][1]), height-1])
    left = max([int(coordinate[0][0]), 0])
    right = min([int(coordinate[1][0]), width-1])
    return image[top:bottom,left:right]

model = training()
last_label = None
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
            edges, cv2.HOUGH_GRADIENT, dp=1, minDist=50, param1=70, param2=50, minRadius=10, maxRadius=200
        )

        # Draw detected circles
        if circles is not None:
            circles = np.uint16(np.around(circles))
            max_circle = None 
            
            for i in circles[0,:]:
                coordinate = [(i[0] - i[2], i[1] - i[2]), (i[0] + i[2], i[1] + i[2])]
                circle_region = cropSign(image, coordinate) 
                
                avg_color = np.mean(circle_region, axis=(0, 1))
                print(avg_color)

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
            cv2.imshow("output.png", sign)

            cv2.circle(image, (max_circle[0], max_circle[1]), max_circle[2], (0, 255, 0), 2)  # Draw the outer circle
            cv2.circle(image, (max_circle[0], max_circle[1]), 2, (0, 0, 255), 3)  # Draw the center of the circle

            label = getLabel(model, sign)
            font = cv2.FONT_HERSHEY_PLAIN

            if label != 0 and label != last_label:
                last_label = label

            if last_label is not None:
                print(SIGNS[last_label])
                font = cv2.FONT_HERSHEY_PLAIN
                cv2.putText(image,SIGNS[last_label],(coordinate[0][0], coordinate[0][1] -15), font, 1,(0,0,255),2,cv2.LINE_4)
        # Display the result
        cv2.imshow('Detected Circles', image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    except Exception as e:
        pass
cv2.destroyAllWindows()
