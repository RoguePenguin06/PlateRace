"""

This code is adapted from OpenCV Course - Full Tutorial with Python
https://www.youtube.com/watch?v=oXlwWbU8l2o&t=56s

"""

import cv2 as cv

img = cv.imread("Resources/Photos/cats.jpg")
cv.imshow("Cats", img)

# converting BGR to Grayscale
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
cv.imshow("Gray", gray)

# blur - gaussian blur
blur =cv.GaussianBlur(img, (7,7), cv.BORDER_DEFAULT)
cv.imshow("Blur", blur)

# edge cascade 
canny = cv.Canny(blur, 125, 175)
cv.imshow("Canny Edges", canny)

# dilating the image
dilated = cv.dilate(canny, (7,7), iterations=3)
cv.imshow("Dilated", dilated)

# eroding
eroded = cv.erode(dilated, (7, 7), iterations=3)
cv.imshow("Eroded", eroded)

cv.waitKey(0)
