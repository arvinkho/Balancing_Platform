"""
Reads frames from the web camera in a separated
thread to increase the calculation speed.

@AUTHOR: Arvin Khodabandeh
@DATE 2019-11-19
"""
import cv2
from threading import Thread


class VideoStream:

    def __init__(self, src=0, height=480, width=640):
        """
        Instanciates the camera thread.
        :param src: the video source (webcam)
        :param height: the pixel height of the frame
        :param width:  the pixel width of the frame
        """
        self.capture_stream = cv2.VideoCapture(src)
        self.capture_stream.set(propId=3, value=width)
        self.capture_stream.set(propId=4, value=height)
        (self.ret, self.frame) = self.capture_stream.read()
        self.stopped = False
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.start()

    def start(self):
        """
        Starts the thread
        """
        self.thread.start()
        return self

    def update(self):
        """
        Updates the frame of the video source
        """
        while True:
            if self.stopped:
                return

            (self.ret, self.frame) = self.capture_stream.read()

    def read(self):
        """
        Reads the last captured frame of the camera
        :return: frame: the last captured frame
        """
        return self.ret, self.frame

    def stop(self):
        """
        Shuts down the camera feed and releases the camera.
        """
        self.stopped = True
        self.capture_stream.release()

    def get_stream(self):
        """
        Returns the actual camera feed
        """
        return self.capture_stream

