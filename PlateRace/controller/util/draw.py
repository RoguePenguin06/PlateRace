"""

This code is adapted from OpenCV Course - Full Tutorial with Python
https://www.youtube.com/watch?v=oXlwWbU8l2o&t=56s

"""

import cv2 as cv
import numpy as np

blank = np.zeros((500, 500, 3), dtype="uint8")
cv.imshow("Blank", blank)

img = cv.imread("Resources/Photos/cats.jpg")
cv.imshow("Cats", img)

# 1. Paint the image a certain color
blank[:] = 0, 0, 255
cv.imshow("Green", blank)

cv.waitKey(0)
