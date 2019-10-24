import cv2
import numpy as np


class BallTracking(object):

    def __init__(self, capture, watch, color="neon_yellow"):
        self.frame = watch
        self.cap = capture
        self.lower_color = np.array([23, 78, 115])
        self.upper_color = np.array([75, 255, 255])
        self.set_color(color)

    def set_color(self, color="neon_yellow"):
        if color == "neon_yellow":
            self.lower_color = np.array([23, 78, 115])
            self.upper_color = np.array([75, 255, 255])

    def get_coordinates(self):
        _, frame = self.cap.read()

        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(hsv, self.lower_color, self.upper_color)
        mask = cv2.erode(mask, None, iterations=2)
        dilation = cv2.dilate(mask, None, iterations=2)

        conts = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        conts = conts[0]
        center = None

        if len(conts) > 0:
            c = max(conts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            center = (cX, cY)

            if self.frame and radius > 10:
                cv2.circle(frame, (int(x), int(y)), int(radius), (255, 0, 255), 2)
                cv2.circle(frame, center, 5, (0, 0, 255), -1)
                cv2.circle(mask, center, 5, (0, 0, 255), -1)
                self.watch(frame, dilation)
            return center

        else:
            if self.frame:
                self.watch(frame, dilation)
            return 0, 0

    @staticmethod
    def watch(frame, dilation):
        cv2.imshow("Frame", frame)
        cv2.imshow("Mask", dilation)

    def stop(self):
        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    cap = cv2.VideoCapture(0)
    cap.set(propId=3, value=640)
    cap.set(propId=4, value=480)
    ballTracking = BallTracking(cap, watch=True, color="neon_yellow")

    while True:
        coordinates = ballTracking.get_coordinates()
        print(coordinates)

        key = cv2.waitKey(5) & 0xFF
        if key == 27:
            ballTracking.stop()
            break
