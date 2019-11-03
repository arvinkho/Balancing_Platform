import cv2
import numpy as np
import argparse as arp
import time
import math
""" locates a maze in a spesific collor and sends it to a pathfinding server, then it returns the resulting path"""
class Maze_Finder:
    def findPath(self, show,cap, dimentions,ballPos,goalPos):
        #get the frame and set the collors
        _, frame = cap.read()
        hsv = cv2.cvtColor(frame, cv2.COLOR_HSV2BGR)

        #find the countrours
        smalColor = np.array([93, 68, 42])
        bigColor = np.array([117, 255, 255])
        blured = cv2.GaussianBlur(hsv,(5,5),5)
        mask = cv2.inRange(blured, smalColor, bigColor)
        contours, hirarky = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        sortedContour = []
        for contour in contours:
            if cv2.contourArea(contour) > 500:
                sortedContour.append(contour)
        cv2.drawContours(frame, sortedContour, -1, (0, 255, 0), thickness=1)
        # set up walls in the maze
        white = np.zeros(shape=[len(frame) - 1, len(frame[0] - 1)], dtype=np.uint8)
        cv2.fillPoly(white,sortedContour,(1))
        cv2.fillPoly(frame, sortedContour, (255, 0, 0))
        # send the maze to the pathfinding and return the result if anny
        if(cv2.getTrackbarPos("col7","frame5") == 1):
            white = cv2.resize(white,(100,100))
            path = client.send_data_to_Astar(white,ballPos,goalPos)
            resizedPath = ([tuple([point[0]*(dimentions[0]/100), point[1]*dimentions[1]/100]) for point in path])
            int(3)
            if resizedPath != None:
                return resizedPath