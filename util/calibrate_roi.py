#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Used to calibrate the region-of-interest
in the capture picture.

@AUTHOR: Arvin Khodabandeh
@DATE: 2019-10-29
"""
import cv2


def nothing(x):
    pass


cap = cv2.VideoCapture(0)
cap.set(propId=3, value=640)
cap.set(propId=4, value=480)

cv2.namedWindow("ROI calibration")
cv2.createTrackbar("X-axis low", "ROI calibration", 0, 640, nothing)
cv2.createTrackbar("X-axis high", "ROI calibration", 0, 640, nothing)
cv2.createTrackbar("Y-axis low", "ROI calibration", 0, 480, nothing)
cv2.createTrackbar("Y-axis high", "ROI calibration", 0, 480, nothing)
cv2.setTrackbarPos("X-axis low", "ROI calibration", 90)
cv2.setTrackbarPos("X-axis high", "ROI calibration", 480)
cv2.setTrackbarPos("Y-axis low", "ROI calibration", 15)
cv2.setTrackbarPos("Y-axis high", "ROI calibration", 360)

while True:

    # get the next frame
    _, frame = cap.read()

    roi_x_l = cv2.getTrackbarPos("X-axis low", "ROI calibration")
    roi_x_h = cv2.getTrackbarPos("X-axis high", "ROI calibration")
    roi_y_l = cv2.getTrackbarPos("Y-axis low", "ROI calibration")
    roi_y_h = cv2.getTrackbarPos("Y-axis high", "ROI calibration")

    roi = frame[roi_y_l:roi_y_h, roi_x_l:roi_x_h]
    frame = cv2.bitwise_and(roi, roi)

    cv2.imshow("Frame", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == 27:
        #TODO: print ROI coordinates
        print("X lower: " + str(roi_x_l))
        print("X upper: " + str(roi_x_h))
        print("Y lower: " + str(roi_y_l))
        print("Y upper: " + str(roi_y_h))
        break


cap.release()
cv2.destroyAllWindows()