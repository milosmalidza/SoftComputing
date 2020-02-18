import cv2
import numpy as np


class Utility:

    video_speed = 1
    absolute_first_frame_index = 60
    square_rect = (250, 200, 410, 450)
    directory = "videos/"

    @staticmethod
    def readImage(frame):
        try:
            return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        except:
            return -1

    @staticmethod
    def getVerticalKernel():
        return np.ones((6, 4), np.uint8)

    @staticmethod
    def contoursMeetsParameters(w, h):
        if (w > 3 and w < 90) and (h > 7 and h < 90):
            return True
        return False

    @staticmethod
    def adaptiveTreshold(frame):
        return cv2.adaptiveThreshold(Utility.readImage(frame), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 15)

    @staticmethod
    def getContourAtPosition(contours, position):
        xx, yy = position
        for c in contours:
            x, y, w, h = c
            if xx == x and yy == y:
                return c

        return None

    @staticmethod
    def checkIfContourIsFree(contour, potential, acquired):
        joined = potential + acquired
        x, y, w, h = contour
        for frame in joined:
            xx, yy = frame.position
            if xx == x and yy == y:
                return False

        return True

    @staticmethod
    def checkRectCollision(rect1, rect2):
        x1, y1, w1, h1 = rect1
        x2, y2, w2, h2 = rect2

        if x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2:
            return True

        return False

    @staticmethod
    def checkIfPotentialIsAcquired(pot, acquired):
        for acq in acquired:
            if acq.position[0] == pot.position[0] and acq.position[1] == pot.position[1]:
                return True
        return False

    @staticmethod
    def getPredictedPeople(width, height):
        wp = round(width / 30)
        wh = round(height / 40)

        if wp == 0: wp = 1
        if wh == 0: wh = 1

        return wp*wh


