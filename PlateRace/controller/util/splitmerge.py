"""

This code is adapted from OpenCV Course - Full Tutorial with Python
https://www.youtube.com/watch?v=oXlwWbU8l2o&t=56s

"""

import cv2 as cv
import numpy as np

img = cv.imread("./Resources/Photos/cats.jpg")
cv.imshow("Cats", img)

blank = np.zeros(img.shape[:2], dtype='uint8')

b, g, r = cv.split(img)

blue = cv.merge([b, blank, blank])
green = cv.merge([blank, g, blank])
red = cv.merge([blank, blank, r])

cv.imshow("Blue", blue)
cv.imshow("Green", green)
cv.imshow("Red", red)

print(img.shape)
print(b.shape)
print(g.shape)
print(r.shape)

merged = cv.merge([b, g, r])
cv.imshow("Merged", merged)

cv.waitKey(0)