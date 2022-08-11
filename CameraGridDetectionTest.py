#!/usr/bin/python3

import cv2
import numpy as np
import time
from functools import *
import random

GREEN = (0, 255, 0)
BLACK = 255
WHITE = 0

DETECTEDNONE = 0
DETECTEDX = 1
DETECTEDO = 2

# Define the camera command
# To flip the image, modify the flip_method parameter (0 and 2 are the most common)
def gstreamer_pipeline(
    capture_width=720, # 1280,
    capture_height=720,
    display_width=720, # 1280,
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

# Shrinks or grows a bounding box by the given factor and Returns the resized BoundingBox
#def scale_bounding_box(boundingBox, scale):
#    x,y,w,h = boundingBox
#    
#    x = int( x + (w * (1 - scale)) )
#    y = int( y + (h * (1 - scale)) )
#    w = int( w * scale )
#    h = int( h * scale )
#    return(x,y,w,h)


# Takes a Bounding Box and works out its position on the board
def bounding_box_position(boundingBox):
    tolerance = 11 # Ignore variations in Y less than this number of pixels
    ret = (boundingBox[1] * tolerance) + (boundingBox[0])
    #print(str(boundingBox[0]) + " " + str(boundingBox[1]) + " " + str(ret))
    return(ret)


# Return a number representing the relative position of a contour
# 0 is top left, maximum result is botton right
def contour_position(contour):
     return(bounding_box_position(cv2.boundingRect(contour)))

# Returns the various properties of passed in contours
def contours_properties(contours):
    print("Number of contours: " + str(len(contours)))
    for contour in contours:
        contour_properties(contour)

def contour_properties(contour):
    peri = cv2.arcLength(contour, True)

    noRawSides = len(contour)

    approx = cv2.approxPolyDP(contour, 0.01 * peri, True)
    noSides = len(approx)

    area = cv2.contourArea(contour)

    print("Perimiter: " + str(int(peri)) + " " + "Number of sides: " + str(int(noSides)) + " Area: " + str(int(area)) + " NO Raw Sides " + str(int(noRawSides)))


# Detect O, X or Nothing in provided contour
def ox_detection(gridContour):

    # Reduce the grid contour to remove the outer box
    gridContour = scale_contour(gridContour, 0.95)

    # Create new image of just the grid square (use exact code as you do in main)

    # Create a mask of the largest contour
    mask = np.zeros((grayI.shape), np.uint8) # Return a new array of zeros of grayI.shape size of type uint8
    # drawcontours(source_image, contours, contours_ID, contour_color, contour_thickness)
    cv2.drawContours(mask, [gridContour], 0, BLACK, -1) # -1 means everything outside the contour
    # Merge the thresholded image and mask
    gridThreshI = cv2.copyTo(threshI, mask)

    # Find contours within image of just the single grid square (copy from main)

    # Each contour is an array of (x,y) coordinates of boundary points of the objects
    oxContours, _ = cv2.findContours(gridThreshI, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # Print out properties of the contours found
    #contours_properties(oxContours)

    # Decide if it is an O, X or none
    if len(oxContours) == 0:
        return(DETECTEDNONE)
    elif len(oxContours) == 1:
        return(DETECTEDX)
    elif len(oxContours) == 2:
        return(DETECTEDO)
    else:
        contours_properties(oxContours)
        return(-1)



# Main
print("--- CAPTURE OPEN START ---")
cap = cv2.VideoCapture(gstreamer_pipeline(), cv2.CAP_GSTREAMER)
print("--- CAPTURE OPEN END ---")
if cap.isOpened():
    print("--- CAMERA IS OPENED ---")
    #window_handle = cv2.namedWindow("CSI Camera", cv2.WINDOW_AUTOSIZE)
    #while cv2.getWindowProperty("CSI Camera", 0) >= 0:
    while 1:
        # Read Camera Image, throwing away first X from buffer
        for _ in range(12):
            ret_val, originalI = cap.read()
        # Grayscale as colour information is not relevant
        grayI = cv2.cvtColor(originalI, cv2.COLOR_BGR2GRAY)
        # Blur image to reduce noise
        blurI = cv2.GaussianBlur(grayI, (7, 7), 0)
        # Threshold image to turn black and white
        # threshI = cv2.adaptiveThreshold(blurI, 255, 1, 1, 11, 2)
        threshI = cv2.adaptiveThreshold(blurI, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv2.THRESH_BINARY_INV, 51, 4)

        #print("Grayscaled, Blured & Thresholded image")
        #cv2.imshow("threshI", threshI)
        #cv2.waitKey(0)
        
        # Find all the contours in the image
        # Each contour is an array of (x,y) coordinates of boundary points of the objects
        contours, _ = cv2.findContours(threshI, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Draw all contours
        #allcontoursI = cv2.drawContours(originalI.copy(), contours, -1, GREEN, 3)
        #print("Contoured image")
        #cv2.imshow("allcontoursI", allcontoursI)
        #cv2.waitKey(0)
        #cv2.destroyWindow("allcontoursI")
        
        # Find the contour with the largest area - ie the outside square of the grid
        # ToDo later - Make this routine safer - 4 sides?
        # Minimum area to consider is 1000
        maxArea = 1000
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > maxArea:
                maxArea = area
                boardContour = contour

        # Increase size of contour so we dont loose outer black box
        boardContour = scale_contour(boardContour, 1.05)

        # Create a mask of the largest contour
        mask = np.zeros((grayI.shape), np.uint8) # Return a new array of zeros of grayI.shape size of type uint8
        # drawcontours(source_image, contours, contours_ID, contour_color, contour_thickness)
        cv2.drawContours(mask, [boardContour], 0, BLACK, -1) # -1 means everything outside the contour
        # Merge the thresholded image and mask
        boardThreshI = cv2.copyTo(threshI, mask)

        #print("Largest contour masked")
        #cv2.imshow("boardThreshI", boardThreshI)
        #cv2.waitKey(0) # Must always waitKey after an imshow, 0 is for a key, or ms
        #cv2.destroyWindow("boardThreshI")

        # Find the contours in the masked image
        contours, _ = cv2.findContours(boardThreshI, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Find the 9 contours of the Noughts and crosses board
        # Find all contours with area greater than X and less than Y
        # Removes any small error contours and and the board contour
        # ToDo later - Make this routine safer and able to cope with different sizes
        gridContours = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 10000 and area < 100000:
                #print(area)
                gridContours.append(contour)


        if len(gridContours) != 9:
            print("ERROR: Not 9 grid squares detected!")
        else:
            print("9 grid squares detected") 

            #gridI = cv2.drawContours(originalI.copy(), gridContours, -1, GREEN, 3
            #print("Nine grid squares image")
            #cv2.imshow("Nine grid squares image", gridI)
            #cv2.waitKey(0) # Must always waitKey after an imshow, 0 is for a key, or ms
            #cv2.destroyWindow("Masked Grid Image")

            # Sort gridContours into the same order as board
            gridContours.sort(key=lambda gC:contour_position(gC))

            for c in range(9):
                print( str(ox_detection(gridContours[c])))

        # Do nothing untill we get an Esc key, and then quit
        while True:
            keyCode = cv2.waitKey(100) # Must always waitKey after an imshow, 0 is for a key, or ms
            if keyCode == 27:
                break
            
    cap.release()
    cv2.destroyAllWindows()
    print("--- Released Camera and Destroyed Windows ---")
else:
    print("--- UNABLE TO OPEN CAMERA ---")
