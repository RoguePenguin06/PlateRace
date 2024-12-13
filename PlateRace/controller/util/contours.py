"""

This code is adapted from OpenCV Course - Full Tutorial with Python
https://www.youtube.com/watch?v=oXlwWbU8l2o&t=56s

Contours are the boundaries of objects, the line or curve that connects the continuous points along the boundary of an object
Not the same as edges from mathematical point of view
Contours are useful for object detection and recognition
"""

import cv2 as cv
import numpy as np

img = cv.imread('./controller.png')
cv.imshow("Controller", img)

blank = np.zeros(img.shape, dtype='uint8')
cv.imshow("Blank", blank)

gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
cv.imshow("Gray", gray)

# This can help with more complex shapes
# blur = cv.GaussianBlur(gray, (5,5), cv.BORDER_DEFAULT)

canny = cv.Canny(img, 125, 175)
cv.imshow("Canny Edges", canny)

# This reduced the contours found. Thresholding binarizes the image ie black or white
ret, thresh = cv.threshold(gray, 125, 255, cv.THRESH_BINARY) 
cv.imshow("Thresh", thresh)

contours, hierarchies = cv.findContours(thresh, cv.RETR_LIST, cv.CHAIN_APPROX_NONE)
print(f'{len(contours)} contour(s) found!')


# draw the contours onto the blank canvas (-1 because we want all the contours), last number is thickness
cv.drawContours(blank, contours, -1, (0,0,255), 2)
cv.imshow("Contours Drawn", blank)

cv.waitKey(0)
