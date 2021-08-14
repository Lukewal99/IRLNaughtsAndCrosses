#!/usr/bin/python3

import cv2
import numpy as np
import time
from functools import *

GREEN = (0, 255, 0)

# Define the camera command
# To flip the image, modify the flip_method parameter (0 and 2 are the most common)
def gstreamer_pipeline(
    capture_width=1280,
    capture_height=720,
    display_width=1280,
    display_height=720,
    framerate=10,
    flip_method=1,
):
    return (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, "
        "format=(string)NV12, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )


# Shrinks or grows a contour by the given factor (float) and Returns the resized contour
def scale_contour(contour, scale):
    moments = cv2.moments(contour)
    midX = int(round(moments["m10"] / moments["m00"]))
    midY = int(round(moments["m01"] / moments["m00"]))
    mid = np.array([midX, midY])
    contour = contour - mid
    contour = (contour * scale).astype(np.int32)
    contour = contour + mid
    return contour


# Main
print("--- CAPTURE OPEN START ---")
cap = cv2.VideoCapture(gstreamer_pipeline(), cv2.CAP_GSTREAMER)
print("--- CAPTURE OPEN END ---")
if cap.isOpened():
    print("--- CAMERA IS OPENED ---")
    # ToDo Why do we need this window?  Can we get rid of it?  Or draw our image in it?
    window_handle = cv2.namedWindow("CSI Camera", cv2.WINDOW_AUTOSIZE)
    # ToDo What does this check for and why
    while cv2.getWindowProperty("CSI Camera", 0) >= 0:
        # Read Camera Image, throwing away first 9 from buffer
        for _ in range(10):
            ret_val, originalI = cap.read()
        # Grayscale as colour information is not relevant
        grayI = cv2.cvtColor(originalI, cv2.COLOR_BGR2GRAY)
        # Blur image to reduce noise
        blurI = cv2.GaussianBlur(grayI, (5,5), 0)
        #cv2.imshow("BlurI", blurI)
        # Threshold - why, what do the numbers mean?
        # How can we reduce interferance here?
        threshI = cv2.adaptiveThreshold(blurI, 255, 1, 1, 11, 2)
        #cv2.imshow("threshI", threshI)
        
        # Find all the contours in the image
        # Each contour is an array of (x,y) coordinates of boundary points of the objects
        contours, _ = cv2.findContours(threshI, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Draw all contours and display
        allcontoursI = cv2.drawContours(originalI.copy(), contours, -1, GREEN, 3)
        #cv2.imshow("allcontoursI", allcontoursI)
        
        # Find the contour with the largest area - ie the outside square of the grid
        # ToDo Make this routine safer - 4 sides?
        # Minimum area to consider is 1000
        max_area = 1000
        for c, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if area > max_area:
                max_area = area
                best_contour = contour
        # Once we've found the largest contour, draw it onto a copy of the original image and display
        largestI = cv2.drawContours(originalI.copy(), contours, c, GREEN, 3)
        #cv2.imshow("largestI", largestI)

        # Increase size of contour so we dont loose outer black box
        best_contour = scale_contour(best_contour, 1.05)

        # Create a mask of the largest contour
        mask = np.zeros((grayI.shape), np.uint8) # Return a new array of zeros of grayI.shape size of type uint8
        cv2.drawContours(mask, [best_contour], 0, 255, -1) # What are these values?
        cv2.drawContours(mask, [best_contour], 0, 0, 2)

        # Merge the image and mask
        maskedI = np.zeros_like(threshI)
        maskedI[mask == 255] = threshI[mask == 255]

        #cv2.imshow("maskedI", maskedI)

        # Create a copy of the original image to draw the final contours on
        finalI = originalI.copy()

        # Find the contours in the masked image
        contours, _ = cv2.findContours(maskedI, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Find all contours with area greater than 100
        gridContours = []
        for contour in contours:
            area = cv2.contourArea(contour)
            # Remove any small imperfections, and the largest box (grid surrounding, as it is drawn out by edges of smaller boxes)
            if area > 100 and area < 100000:
                gridContours.append(contour)
                #time.sleep(1)
                #cv2.waitKey(0)
                finalI = cv2.drawContours(finalI, [contour], -1, GREEN, 3)
                #cv2.imshow("Final Image", finalI)

        if len(gridContours) != 9:
            print("ERROR: Not 9 grid squares detected!")
        else:
         #   finalI = cv2.drawContours(finalI, gridContours, -1, GREEN, 3)
            # Show the last image
            cv2.imshow("Final Image", finalI)

            avg = reduce(
                lambda total, arr : total + arr[0] ,
                gridContours)

            print("avg: " + avg) 

            # todo sort grid squares into same order as board
            contourCentres = []
            for contour in gridContours:
                contourXTotal = 0
                contourYTotal = 0
                for xy in contour:
                    contourXTotal = contourXTotal + xy[0][0]
                    contourYTotal = contourYTotal + xy[0][1]
                contourXAvg = contourXTotal / len(contour)
                contourYAvg = contourYTotal / len(contour)
                print(str(contourXAvg) + " " + str(contourYAvg))
                #contourCentres.append([contourXAvg,contourYAvg])
                

        time.sleep(1)
            #cv2.waitKey(0)
            
        # This also acts as (Copied notes - what does this mean? -Luke)
        keyCode = cv2.waitKey(30) & 0xFF
        # Stop the program on the ESC key
        if keyCode == 27:
            break
    cap.release()
    cv2.destroyAllWindows()
else:
    print("--- UNABLE TO OPEN CAMERA ---")
