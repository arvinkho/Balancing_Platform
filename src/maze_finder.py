import cv2
import numpy as np

""" locates a maze in a spesific color and sends it to a pathfinding server, then it returns the resulting path
    author: fredborg
    version: 1
"""


class Maze_Finder:
    ''' sends an maze to a star server and then the a star solves that. returns the astar and then returns the path

    '''

    def findPath(self, client, cap, ballPos, goalPos):

        dimentions = (400, 400)

        # get the frame and set the collors
        _, frame = cap.read()
        roi = frame[64:464, 116:516]
        frame = cv2.bitwise_and(roi, roi)
        print(frame.size)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # find the countrours
        smalColor = np.array([100, 79, 98])
        bigColor = np.array([119, 183, 200])
        blured = cv2.GaussianBlur(hsv, (5, 5), 5)
        mask = cv2.inRange(blured, smalColor, bigColor)
        contours, hirarky = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        self.showImage(frame, mask)
        # sort the countrours and discard the smalest ones.
        sortedContour = []
        for contour in contours:
            if cv2.contourArea(contour) > 50:
                sortedContour.append(contour)
        cv2.drawContours(frame, sortedContour, -1, (0, 255, 0), thickness=1)

        # # set up walls in the maze
        whiteMask = np.zeros(shape=frame.shape, dtype=np.uint8)
        mask = cv2.resize(mask,(100,100))



        # cv2.drawContours(whiteMask, sortedContour, -1, (1), thickness=3)
        # cv2.fillPoly(whiteMask, sortedContour, 1)
        cv2.fillPoly(frame, sortedContour, (0, 255, 0))

        # send the maze to the pathfinding and return the result if anny

        ballPos = ([integer // 4 for integer in ballPos])
        goalPos = ([integer // 4 for integer in goalPos])


        path = client.send_data_to_Astar(mask, ballPos, goalPos)

        #self.showImage(frame, whiteMask)
        if not path is None:
            resizedPath = (
                [list([int(point[0] * (dimentions[0] / 100)), int(point[1] * (dimentions[1] / 100))]) for point in
                 path])
            resizedPath.reverse()
            print(resizedPath)
            return (resizedPath)

    def showImage(self, frame1, frame2):
        cv2.imshow("frame", frame1)
        cv2.imshow("frame1", frame2)
