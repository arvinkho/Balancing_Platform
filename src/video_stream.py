import cv2
import numpy as np
from threading import Thread
import time



class VideoStream():

    def __init__(self, src=0, height=480, width=640):

        self.capture_stream = cv2.VideoCapture(src)
        self.capture_stream.set(propId=3, value=width)
        self.capture_stream.set(propId=4, value=height)
        (self.ret, self.frame) = self.capture_stream.read()
        self.stopped = False
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.start()

    def start(self):

        self.thread.start()
        return self

    def update(self):
        while True:
            if self.stopped:
                return

            (self.ret, self.frame) = self.capture_stream.read()

    def read(self):

        return self.ret, self.frame

    def stop(self):
        self.stopped = True

    def get_stream(self):
        return self.capture_stream
