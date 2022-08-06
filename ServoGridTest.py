#!/usr/bin/python3

# MUST SET UP AS UNIX IN NP++

# Import
import RPi.GPIO as GPIO
from adafruit_servokit import ServoKit
import time
import random
import NaughtsAndCrossesLib as NaC
import math as maths
import signal

# Variables
laserPointerPin = "DAP4_SCLK" # BCM pin 18, BOARD pin 12
X = 0
Y = 1

# Absolute middle of grid (ie middle of position 4)
startX = 97
startY = 50

# Distance to step to other grid positions
stepX = 23
stepY = 17

# Size of X and O
radiusX = stepX * 0.45
radiusY = stepY * 0.45

# Speed factor for testing
speed = 3

# Starting Top Left {0} -> Bottom Right {8}
grid = ((startX+stepX, startY+stepY), (startX, startY+stepY), (startX-stepX, startY+stepY),
        (startX+stepX, startY),             (startX, startY),       (startX-stepX, startY),
        (startX+stepX, startY-stepY), (startX, startY-stepY), (startX-stepX, startY-stepY))

# Functions
# Setup
def setup():
    global kit
    kit = ServoKit(channels=16)
    #print(GPIO.getmode())
    #GPIO.setmode(GPIO.BCM)  # BCM pin-numbering scheme from Raspberry Pi
    GPIO.setup(laserPointerPin, GPIO.OUT, initial=GPIO.LOW) # Set pin as an output pin with optional initial state of LOW
    # Catch ^C etc and exit gracefully
    signal.signal(signal.SIGINT, handler)


# Point Laser at each square of the grid in turn to check alignment
def testGrid():
    print("Test Grid")
    for gridPosition in grid:
        print(" x / y " + str(gridPosition[X]) + " / " + str(gridPosition[Y]))
        kit.servo[X].angle=gridPosition[X]
        kit.servo[Y].angle=gridPosition[Y]
        time.sleep(0.2) # Wait till we get to position
        GPIO.output(laserPointerPin, GPIO.HIGH) # Turn ON pointer
        time.sleep(0.5 * speed)
        GPIO.output(laserPointerPin, GPIO.LOW) # Turn OFF pointer


# Draw an O with the Laser at the specified gridXY
def drawO(gridXY):
    print("Draw O")
    # Move to start position
    x = radiusX * maths.cos(0)
    y = radiusY * maths.sin(0)
    print(" x / y " + str(x) + " / " + str(y))
    kit.servo[X].angle = x + gridXY[0]
    kit.servo[Y].angle = y + gridXY[1]
    time.sleep(0.2 * speed)

    # ToDo Dont go to Start position twice, make sure end position is 1 before start pos?
    GPIO.output(laserPointerPin, GPIO.HIGH) # Turn ON pointer
    time.sleep(0.02 * speed)

    for radians in range(0,int(2 * maths.pi * 10)+2):
        x = radiusX * maths.cos(radians / 10)
        y = radiusY * maths.sin(radians / 10)
        print(" x / y " + str(x) + " / " + str(y))
        kit.servo[X].angle = x + gridXY[0]
        kit.servo[Y].angle = y + gridXY[1]
        time.sleep(0.02 * speed)
    GPIO.output(laserPointerPin, GPIO.LOW) # Turn OFF pointer


# Draw an X with the Laser at the specified gridXY
def drawX(gridXY):
    print("Draw X")
    # Top left starting pos
    x = radiusX * (-10 / 10)
    y = radiusY * (-10 / 10)
    print(" x / y " + str(x) + " / " + str(y))
    kit.servo[X].angle = gridXY[X] - x
    kit.servo[Y].angle = gridXY[Y] - y
    time.sleep(0.07 * speed) # Time to position from bottom left to top left
    GPIO.output(laserPointerPin, GPIO.HIGH) # Turn ON pointer
    time.sleep(0.017 * speed)

    # Scan top left to bottom right
    for i in range(-9, 11):
        x = radiusX * (i / 10)
        y = radiusY * (i / 10)
        print(" x / y " + str(x) + " / " + str(y))
        kit.servo[X].angle = gridXY[X] - x
        kit.servo[Y].angle = gridXY[Y] - y
        time.sleep(0.017 * speed)
    GPIO.output(laserPointerPin, GPIO.LOW) # Turn OFF pointer
   

     # Top right starting pos
    x = radiusX * (-10 / 10)
    y = radiusY * (-10 / 10)
    print(" x / y " + str(x) + " / " + str(y))
    kit.servo[X].angle = gridXY[X] + x
    kit.servo[Y].angle = gridXY[Y] - y
    time.sleep(0.2 * speed) # Time to position from anywhere on the grid
    GPIO.output(laserPointerPin, GPIO.HIGH) # Turn ON pointer
    time.sleep(0.017 * speed)

    # Scan top right to bottom left
    for i in range(-9, 11):
        x = radiusX * (i / 10)
        y = radiusY * (i / 10)
        print(" x / y " + str(x) + " / " + str(y))
        kit.servo[X].angle = gridXY[X] + x
        kit.servo[Y].angle = gridXY[Y] - y
        time.sleep(0.017 * speed)
    GPIO.output(laserPointerPin, GPIO.LOW) # Turn OFF pointer


def handler(signum, frame):
    GPIO.output(laserPointerPin, GPIO.LOW) # Turn OFF pointer
    exit(1)

# Main
def main():
    setup()
    testGrid()
    time.sleep(1)
    #drawO(grid[4])
    #drawX(grid[4])
    time.sleep(1)
    for j in range(9): drawX(grid[j])
    for k in range(9): drawO(grid[k])
    GPIO.cleanup()


if __name__ == '__main__':
    main()
