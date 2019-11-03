import cv2
import numpy as np
import argparse as arp
import path3_1 as path
import time
import math
import path3 as AStar

class pathing:

    def nothing(self,x):
        pass

    def createSlidershow(self):
        cap = cv2.VideoCapture(1)
        cv2.namedWindow("frame5")
        cv2.createTrackbar("col1", "frame5", 0, 255, nothing)

        cv2.createTrackbar("col2", "frame5", 0, 255, nothing)

        cv2.createTrackbar("col3", "frame5", 0, 255, nothing)

        cv2.createTrackbar("col4", "frame5", 255, 255, nothing)

        cv2.createTrackbar("col5", "frame5", 255, 255, nothing)

        cv2.createTrackbar("col6", "frame5", 130, 255, nothing)

        cv2.createTrackbar("col7", "frame5", 0,1,nothing)



    def findPath(self, show,cap,client):
        while True:
            _, frame = cap.read()
            hsv = cv2.cvtColor(frame, cv2.COLOR_HSV2BGR)

            col1 = cv2.getTrackbarPos("col1", "frame5")
            col2 = cv2.getTrackbarPos("col2", "frame5")
            col3 = cv2.getTrackbarPos("col3", "frame5")
            col4 = cv2.getTrackbarPos("col4", "frame5")
            col5 = cv2.getTrackbarPos("col5", "frame5")
            col6 = cv2.getTrackbarPos("col6", "frame5")

            smalColor = np.array([col1, col2, col3])
            bigColor = np.array([col4, col5, col6])
            blured = cv2.GaussianBlur(hsv,(5,5),5)
            white = np.zeros(shape=[len(frame) - 1, len(frame[0] - 1)], dtype=np.uint8)

            mask = cv2.inRange(blured, smalColor, bigColor)
            contours, hirarky = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            sortedContour = []
            for contour in contours:
                if cv2.contourArea(contour) > 500:
                    sortedContour.append(contour)
            cv2.drawContours(frame, sortedContour, -1, (0, 255, 0), thickness=1)
            cv2.fillPoly(white,sortedContour,(1))
            cv2.fillPoly(frame, sortedContour, (255, 0, 0))
            if(cv2.getTrackbarPos("col7","frame5") == 1):
                white = cv2.resize(white,(100,100))
                sti = client.send_data_to_Astar(white,(0,0),(99,99))
                prevPoint= (0,0)
                frame= cv2.resize(frame,(1000,1000))
                bigPath = ([tuple([pa*10 for pa in point]) for point in sti])
                for points in bigPath:
                    cv2.line(frame, points,prevPoint,(0,255,0), thickness= 2)
                    prevPoint = points
            if(show):
                cv2.imshow("frame", frame)
                cv2.imshow("frame2", mask)
            key = cv2.waitKey(1)
            if key == 27:
                break
        cap.release()
        cv2.destroyAllWindows()
pathing = pathing()
pathing.createSlidershow()
pathing.findPath(True)