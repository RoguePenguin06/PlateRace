"""

This code is adapted from OpenCV Course - Full Tutorial with Python
https://www.youtube.com/watch?v=oXlwWbU8l2o&t=56s

"""

import cv2 as cv

# # read image
# img = cv.imread('Resources/Photos/cat.jpg')

# # show image
# cv.imshow('cat', img)

# # wait infinite amout of time for keyboard key to be pressed
# cv.waitKey(0)


capture = cv.VideoCapture('Resources/Videos/dog.mp4')

while True:
    isTrue, frame = capture.read()
    cv.imshow('Video', frame)

    if cv.waitKey(20) & 0xFF == ord('d'):
        break

capture.realease()
cv.destroyAllWindows()