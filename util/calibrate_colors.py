#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A tool used for getting the correct upper
and lower HSV values of a given color. Features
a interactive GUI with value adjustments on-the-fly.

@AUTHOR: Arvin Khodabandeh
@DATE: 2019-10-24
"""

import cv2
import numpy as np


def nothing(x):
    pass


cap = cv2.VideoCapture(1)
cap.set(propId=3, value=640)
cap.set(propId=4, value=480)

cv2.namedWindow("Color calibration")
cv2.createTrackbar("H-value_low", "Color calibration", 0, 179, nothing)
cv2.createTrackbar("H-value_high", "Color calibration", 0, 179, nothing)
cv2.createTrackbar("S-value_low", "Color calibration", 0, 255, nothing)
cv2.createTrackbar("S-value_high", "Color calibration", 0, 255, nothing)
cv2.createTrackbar("V-value_low", "Color calibration", 0, 255, nothing)
cv2.createTrackbar("V-value_high", "Color calibration", 0, 255, nothing)

while True:

    # get the next frame
    _, frame = cap.read()

    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    # get values from the track bar
    l_h = cv2.getTrackbarPos("H-value_low", "Color calibration")
    u_h = cv2.getTrackbarPos("H-value_high", "Color calibration")
    l_s = cv2.getTrackbarPos("S-value_low", "Color calibration")
    u_s = cv2.getTrackbarPos("S-value_high", "Color calibration")
    l_v = cv2.getTrackbarPos("V-value_low", "Color calibration")
    u_v = cv2.getTrackbarPos("V-value_high", "Color calibration")

    # set upper and lower bounds in the HSV range
    lower_color = (l_h, l_s, l_v)
    upper_color = (u_h, u_s, u_v)

    # Perform blurring on the parts of the image within the HSV values
    mask = cv2.inRange(hsv, lower_color, upper_color)
    mask = cv2.erode(mask, None, iterations=2)
    dilation = cv2.dilate(mask, None, iterations=2)

    # Find contours of the blurred image
    conts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    conts = conts[0]
    center = None


    if len(conts) > 0:
        c = max(conts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        if (int(M["m00"])) != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            center = (cX, cY)

        if radius > 10:
            cv2.circle(frame, (int(x), int(y)), int(radius), (255, 0, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)

    cv2.imshow("frame", frame)
    cv2.imshow("mask", dilation)
    key = cv2.waitKey(100) & 0xFF
    if key == 27:
        print("Lower colors (HSV): " + str(lower_color))
        print("Upper colors (HSV): " + str(upper_color))
        break


cap.release()
cv2.destroyAllWindows()
