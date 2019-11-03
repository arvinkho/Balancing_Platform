import cv2
import numpy as np

""" locates a maze in a spesific color and sends it to a pathfinding server, then it returns the resulting path"""


class Maze_Finder:
    def findPath(self,client, cap, ballPos, goalPos):


        dimentions = (400, 400)


        # get the frame and set the collors
        _, frame = cap.read()
        roi = frame[64:464, 116:516]
        frame = cv2.bitwise_and(roi, roi)
        hsv = cv2.cvtColor(frame, cv2.COLOR_HSV2BGR)

        # find the countrours
        smalColor = np.array([93, 68, 42])
        bigColor = np.array([117, 255, 255])
        blured = cv2.GaussianBlur(hsv, (5, 5), 5)
        mask = cv2.inRange(blured, smalColor, bigColor)
        contours, hirarky = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # sort the countrours and discard the smalest ones.
        sortedContour = []
        for contour in contours:
            if cv2.contourArea(contour) > 250:
                sortedContour.append(contour)
        cv2.drawContours(frame, sortedContour, -1, (0, 255, 0), thickness=1)

        # set up walls in the maze
        white = np.zeros(shape=[len(frame) - 1, len(frame[0] - 1)], dtype=np.uint8)
        cv2.fillPoly(white, sortedContour, (1))
        cv2.fillPoly(frame, sortedContour, (255, 0, 0))

        # send the maze to the pathfinding and return the result if anny
        white = cv2.resize(white, (100, 100))

        print(type(white))

        ballPos = (ints % 4 for ints in ballPos)
        goalPos = (ints % 4 for ints in goalPos)

        path = client.send_data_to_Astar(white, ballPos, goalPos)
        resizedPath = ([
            tuple([point[0] * (dimentions[0] / 100), point[1] * (dimentions[1] / 100)]) for point in path])
        if not resizedPath is None:
            return (self.reduce_path(),resizedPath)

        """finds all points on the same line and simplifies the path to only points that are not on the same line"""

    def reduce_path(self, path):
        last_vector = [path[0], path[1]]
        last_point = path[0]
        vectors = [(last_vector)]
        i = 0
        newPath = [path[0]]
        for points in path:
            if (last_vector[0][0] - last_vector[1][0]) / (last_vector[0][1] - last_vector[1][1]) == \
                    (last_vector[0][0] - points[0]) / (last_vector[0] - [1] - points[1]):
                vectors[i][1] = points
            else:
                vectors.append((last_point)(points))
                last_vector = ((last_point)(points))
                newPath.append(points)
            last_point = points
        return newPath

