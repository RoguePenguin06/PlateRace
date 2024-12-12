"""

This code is adapted from OpenCV Course - Full Tutorial with Python
https://www.youtube.com/watch?v=oXlwWbU8l2o&t=56s

"""
import cv2 as cv
import numpy as np

img = cv.imread("Resources/Photos/cats.jpg")

# Translation
def translate(img, x, y):
    # -x --> Left
    # -y --> Up
    # x --> Right
    # y --> Down
    transMat = np.float32([[1,0,x],[0,1,y]])
    dimensions = (img.shape[1], img.shape[0])
    return cv.warpAffine(img, transMat, dimensions)

translated = translate(img, -100, 100)
cv.imshow("Translated", translated)


# Rotation
def rotate(img, angle, rotPoint=None):
    (height, width) = img.shape[:2]

    if rotPoint is None:
        rotPoint = (width//2, height//2)

    rotMat = cv.getRotationMatrix2D(rotPoint, angle, 1.0)
    dimensions = (width, height)

    return cv.warpAffine(img, rotMat, dimensions)

rotated = rotate(img, -45)
cv.imshow("Rotated", rotated)

rotated_rotated = rotate(rotated, -45)
cv.imshow("Rotated Rotated", rotated_rotated)

# Resizing
resized = cv.resize(img, (500, 500), interpolation=cv.INTER_CUBIC)
cv.imshow("Resized", resized)

# Flipping # TODO use for mirror driving
def flip(img, flipCode=1):
    return cv.flip(img, flipCode)
flip = flip(img)
cv.imshow("Flip", flip)

# Cropping
cropped = img[200:400, 300:400]
cv.imshow("Cropped", cropped)

cv.waitKey(0)