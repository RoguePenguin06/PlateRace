"""

This code is adapted from OpenCV Course - Full Tutorial with Python
https://www.youtube.com/watch?v=oXlwWbU8l2o&t=56s

Use where the lighting or similar causes the image to be unclear

"""

import cv2 as cv
import numpy as np

img = cv.imread("./Resources/Photos/cats.jpg")
cv.imshow("Cats", img)

# Define Kernel or Window that is drawn over the image
# The example is 3x3. Something happens to the middle pixel as a result of the pixels surrounding it.
average = cv.blur(img, (3,3))
cv.imshow("Average Blur", average)

# Gaussian Blur
# Gives each surrounding pixel a weight.
gauss = cv.GaussianBlur(img, (3, 3), 0)
cv.imshow("Gaussian Blur", gauss)

# Median Blur
# Similar to averaging, just finds median of surrounding pixels instead.
# More effective in reducing noise.
median = cv.medianBlur(img, 3)
cv.imshow("Median Blur", median)

# Bilateral Blur
# Most effective. Applies blur but retains edges.
# Sigma space sets how far away you want the pixels to consider other pixels
# Large values make it more like median blur 
bilateral = cv.bilateralFilter(img, 10, 35, 25)
cv.imshow("Bilateral Blur", bilateral)

cv.waitKey(0)