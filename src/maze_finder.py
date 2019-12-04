import cv2
import numpy as np

""" locates a maze in a spesific color and sends it to a pathfinding server, then it returns the resulting path
    author: fredborg
    version: 1
"""


class MazeFinder(object):

    def __init__(self, client, capture, roi_size_x, roi_size_y):
        """
        creates an instance of the maze finder and defines the size of the window to be used.
        in adition it defines the capture frame and the client that we send the data to for solving.
        :param client: the UDP client that the java dock comunicates.
        :param capture: the capture frame of the camera.
        :param roi_size_x: the downsized x dimentions of the frame.
        :param roi_size_y: the downsized x dimentions of the frame.
        """
        self.client = client
        self.cap = capture
        self.roi_size_x = roi_size_x
        self.roi_size_y = roi_size_y




    def find_path(self, ball_pos, goal_pos):
        """
            sends an maze to a star server and then the a star solves that. returns the astar and then returns the path
            :param ball_pos the strart possition for the maze solving
            :param goal_pos the end possition for the maze solving
            :return an array of points representing the maze form start to stopp.
        """

        dimensions = (400, 400)

        # get the frame and set the colors
        _, frame = self.cap.read()
        roi = frame[self.roi_size_y[0]:self.roi_size_y[1], self.roi_size_x[0]:self.roi_size_x[1]]
        frame = cv2.bitwise_and(roi, roi)

        # find the contours
        small_color = np.array([100, 5, 64])
        big_color = np.array([160, 188, 255])
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, small_color, big_color)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=10)
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        # self.show_image(frame, mask)

        # sort the contours and discard the smallest ones.
        sorted_contour = []
        for contour in contours:
            if cv2.contourArea(contour) > 50:
                sorted_contour.append(contour)
        cv2.drawContours(frame, sorted_contour, -1, (0, 255, 0), thickness=1)

        # set up walls in the maze
        whiteMask = np.zeros(shape=frame.shape, dtype=np.uint8)
        mask = cv2.resize(mask, (100, 100))

        # cv2.drawContours(whiteMask, sortedContour, -1, (1), thickness=3)
        # cv2.fillPoly(whiteMask, sortedContour, 1)
        cv2.fillPoly(frame, sorted_contour, (0, 255, 0))

        # send the maze to the pathfinding and return the result if anny

        ball_pos = ([integer // 4 for integer in ball_pos])
        goal_pos = ([integer // 4 for integer in goal_pos])

        if ball_pos != goal_pos:
            path = self.client.send_data_to_Astar(mask, ball_pos, goal_pos)
        else:
            path = None
            print("ball pos and goal pos can not be the same!")

        # self.showImage(frame, whiteMask)
        if path is not None:
            resized_path = (
                [list([int(point[0] * (dimensions[0] / 100)), int(point[1] * (dimensions[1] / 100))]) for point in
                 path])
            resized_path.reverse()
            # print(resized_path)
            return resized_path

    def show_image(self, frame1, frame2):
        """
        if called showes the image on the users computer screen.
        :param frame1: the first frame to bre shown, next to frame 2.
        :param frame2: the second frame to bre shown, next to frame 1.
        :return:
        """
        cv2.imshow("frame", frame1)
        cv2.imshow("frame1", frame2)
