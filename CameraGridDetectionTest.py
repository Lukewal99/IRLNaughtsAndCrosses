#!/usr/bin/python3

import cv2
import numpy as np
import time
from functools import *
import random

GREEN = (0, 255, 0)
BLACK = 255
WHITE = 0

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

def scale_bounding_box(boundingBox, scale):
    x,y,w,h = boundingBox
    
    x = int( x + (w * (1 - scale)) )
    y = int( y + (h * (1 - scale)) )
    w = int( w * scale )
    h = int( h * scale )
    return(x,y,w,h)


    
# Takes a contour and works out its position on the board
#def contour_position(contour):
#    moments = cv2.moments(contour)
#    midX = moments["m10"] / moments["m00"]
#    midY = moments["m01"] / moments["m00"]
#    tolerance = 50 # Ignore variations in Y less than this number of pixels
#    ofset = 20 # Hack to overcome fixed boundaries of tolerance
#    # Test Code to prove working
#    #return random.randint(0,100)
#    r = (((1000 - midY + ofset) // tolerance) * tolerance) + midX
#    print(str(midX) + " " + str(midY) + " " + str(r))
#    return(r)

# Takes a Bounding Box and works out its position on the board
# Seems to work, but needs further testing and making more robust
def bounding_box_position(boundingBox):
    tolerance = 11 # Ignore variations in Y less than this number of pixels
    ret = (boundingBox[1] * tolerance) + (boundingBox[0])
    #print(str(boundingBox[0]) + " " + str(boundingBox[1]) + " " + str(ret))
    return(ret)

def ox_detection(boundingBox, testName):
    # Reduces the bounding box to remove post-it note
    x,y,w,h = scale_bounding_box(boundingBox, 0.9)
    print("x: " + str(x) + "y: " + str(y) + "w: " + str(w) + "h: " + str(h))

    # Create a mask of the largest contour
    mask = np.zeros((grayI.shape), np.uint8) # Return a new array of zeros of grayI.shape size of type uint8
    cv2.rectangle(mask, (x,y), (x+w,y+h), BLACK, -1)

    # Merge the image and mask
    maskedThreshI = cv2.copyTo(threshI, mask)
    maskedOriginalI = cv2.copyTo(originalI, mask)
    #cv2.imshow(testName, maskedI)

    #Find the contour of the shape inside the bounding box
    contours, _ = cv2.findContours(maskedThreshI, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    allcontoursI = cv2.drawContours(maskedOriginalI.copy(), contours, -1, GREEN, 3)
    cv2.imshow(testName, allcontoursI)

    #starting minimum
    max_area = 0
    for c, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if area > max_area:
            max_area = area
            largest_contour = contour

    # TO DO NEXT -----------------------------------------------------------------------
    # Change Bounding Boxes for Contours - to help eliminate outer boundary with scaling
    # Or De-warp image early

# Main
print("--- CAPTURE OPEN START ---")
cap = cv2.VideoCapture(gstreamer_pipeline(), cv2.CAP_GSTREAMER)
print("--- CAPTURE OPEN END ---")
if cap.isOpened():
    print("--- CAMERA IS OPENED ---")
    #window_handle = cv2.namedWindow("CSI Camera", cv2.WINDOW_AUTOSIZE)
    #while cv2.getWindowProperty("CSI Camera", 0) >= 0:
    while 1:
        # Read Camera Image, throwing away first 9 from buffer
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

        #cv2.imshow("threshI", threshI)
        #cv2.waitKey(0)
        
        # Find all the contours in the image
        # Each contour is an array of (x,y) coordinates of boundary points of the objects
        contours, _ = cv2.findContours(threshI, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Draw all contours and display
        allcontoursI = cv2.drawContours(originalI.copy(), contours, -1, GREEN, 3)
        cv2.imshow("allcontoursI", allcontoursI)
        cv2.waitKey(0)
        cv2.destroyWindow("allcontoursI")
        
        # Find the contour with the largest area - ie the outside square of the grid
        # ToDo Make this routine safer - 4 sides?
        # Minimum area to consider is 1000
        max_area = 1000
        for c, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if area > max_area:
                max_area = area
                best_contour = contour

        # Increase size of contour so we dont loose outer black box
        best_contour = scale_contour(best_contour, 1.05)

        # Create a mask of the largest contour
        mask = np.zeros((grayI.shape), np.uint8) # Return a new array of zeros of grayI.shape size of type uint8
        # drawcontours(source_image, contours, contours_ID, contour_color, contour_thickness)
        cv2.drawContours(mask, [best_contour], 0, BLACK, -1) # -1 means everything outside the contour
        #cv2.drawContours(mask, [best_contour], 0, WHITE, 2) 

        # Merge the thresholded image and mask
        #maskedI = np.zeros_like(threshI)
        #maskedI[mask == 255] = threshI[mask == 255]
        maskedI = cv2.copyTo(threshI, mask)

        cv2.imshow("maskedI", maskedI)
        cv2.waitKey(0)# Must always waitKey after an imshow, 0 is for a key, or ms
        cv2.destroyWindow("maskedI")

        # Find the contours in the masked image
        contours, _ = cv2.findContours(maskedI, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Find all contours with area greater than X and less than Y
        # Removes any small error contours and and the largest box (grid surrounding, as it is drawn out by edges of smaller boxes)
        gridContours = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 10000 and area < 100000:
                #print(area)
                gridContours.append(contour)

        # Simplify gridContours into gridBoundingBoxes
        gridBoundingBoxes = [cv2.boundingRect(c) for c in gridContours]

        print(gridBoundingBoxes)

        if len(gridBoundingBoxes) != 9:
            print("ERROR: Not 9 grid squares detected!")
        else:
            gridI = cv2.drawContours(originalI.copy(), gridContours, -1, GREEN, 3)
            cv2.imshow("Masked Grid Image", gridI)
            cv2.waitKey(0)# Must always waitKey after an imshow, 0 is for a key, or ms
            cv2.destroyWindow("Masked Grid Image")

            # Sort gridContours into the same order as board
            gridBoundingBoxes.sort(key=lambda bb:bounding_box_position(bb))
           
            print(gridBoundingBoxes)
            print()

            # todo sort grid squares into same order as board
            #gridContoursAverage = []
            #for c, contour in enumerate(gridContours):
            #    contourXTotal = 0
            #    contourYTotal = 0
            #    for xy in contour:
            #        contourXTotal = contourXTotal + xy[0][0]
            #        contourYTotal = contourYTotal + xy[0][1]
            #    contourXAvg = contourXTotal / len(contour)
            #    contourYAvg = contourYTotalx_detection / len(contour)
            #    print("ContourXY Averages: " + str(contourXAvg) + " " + str(contourYAvg))
            #    gridContours[c] = [contour, [contourXAvg, contourYAvg] ]

            ox_detection(gridBoundingBoxes[0], "Small Grid 0")
            ox_detection(gridBoundingBoxes[1], "Small Grid 1")
            ox_detection(gridBoundingBoxes[2], "Small Grid 2") 

            cv2.waitKey(0)
            
        # This also acts as (Copied notes - what does this mean? -Luke)
        #keyCode = cv2.waitKey(30) & 0xFF
        # Stop the program on the ESC key
        #if keyCode == 27:
        #    break
    cap.release()
    cv2.destroyAllWindows()
else:
    print("--- UNABLE TO OPEN CAMERA ---")
