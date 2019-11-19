#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Processes an image and isolates, masks and
creates a contour around the largest
object with the corresponding color space. The
masking is done with HSV-colors. Returns the X and Y
coordinates of the centroid of the masked contour.

@AUTHOR: Arvin Khodabandeh
@DATE: 2019-10-24
"""

import cv2
import numpy as np
import time


class BallTracking(object):

    def __init__(self, capture, watch, roi_size_x=(128, 528), roi_size_y=(40, 440),
                 color="neon_yellow"):
        """
        Finds the largest object within the HSV
        color limits. Returns the centroid coordinates
        (X and Y).
        :param capture: the video source (webcam)
        :param watch: boolean value to indicate if the picture should
        be shown. True: show picture.
        :param color: pre-defined upper and lower HSV values
        """
        self.draw_image = watch
        self.cap = capture
        self.lower_color = np.array([23, 78, 115])
        self.upper_color = np.array([75, 255, 255])
        self.set_color(color)
        self.roi_size_x = roi_size_x
        self.roi_size_y = roi_size_y

    def set_color(self, color="neon_yellow"):
        """
        Set the color of the object to track.
        """
        if color == "neon_yellow":
            self.lower_color = np.array([23, 78, 115])
            self.upper_color = np.array([75, 255, 255])
        elif color == "red":
            self.lower_color = np.array([0, 42, 142])
            self.upper_color = np.array([13, 255, 255])
        elif color == "pink":
            self.lower_color = np.array([150, 40, 40])
            self.upper_color = np.array([179, 255, 255])

    def get_coordinates(self):
        """
        Mask, erode and dilate an image with HSV values
        within given limits. If an object within the correct
        HSV values are found, get and return the coordinates of
        the objects centroid (X, Y).

        :return: If an object is found, return the coordinates (X and Y)
        of the centroid. If no object is found, return (0, 0)
        """
        _, frame = self.cap.read()

        roi = frame[self.roi_size_y[0]:self.roi_size_y[1], self.roi_size_x[0]:self.roi_size_x[1]]
        frame = cv2.bitwise_and(roi, roi)

        blurred = cv2.GaussianBlur(frame, (5, 5), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(hsv, self.lower_color, self.upper_color)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        conts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        conts = conts[0]
        center = None

        if len(conts) > 0:
            c = max(conts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            center = (cX, cY)

            if self.draw_image and radius > 5:
                cv2.circle(frame, (int(x), int(y)), int(radius), (255, 0, 255), 2)
                cv2.circle(frame, center, 5, (0, 0, 255), -1)
                self.watch(frame, mask)
            return center

        else:
            if self.draw_image:
                self.watch(frame, mask)
            return 0, 0



    @staticmethod
    def watch(frame, mask):
        """
        Show the captured image and the masked image.
        """
        cv2.imshow("Frame", frame)
        cv2.imshow("Mask", mask)

    def stop(self):
        """
        Shut down the video capturing and close all
        the opened windows (if any).
        """
        self.cap.stop()
        cv2.destroyAllWindows()


# A simple example to show the functionality of this class.

if __name__ == '__main__':
    cap = cv2.VideoCapture(1)
    cap.set(propId=3, value=640)
    cap.set(propId=4, value=480)
    ballTracking = BallTracking(cap, watch=False, color="pink")
    prev_time = 0
    while True:
        current_time = time.time()
        coordinates = ballTracking.get_coordinates()
        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            ballTracking.stop()
            break
        print((current_time - prev_time) * 1000)
        prev_time = current_time

