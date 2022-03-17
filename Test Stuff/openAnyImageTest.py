"""
Author: Alexander Goudemond

Program name: openAnyImageTest.py

Goal: Open a test image, using OpenCV, and display 3 forms: grayscale, colour and unchanged


Notes:
OpenCV seems to be a popular vision library

3 built-in functions: imread(), imshow(), imwrite()
imshow() designed to be used with destroyAllWindows() / destroyWindow() functions
"""

print("Hello World! Here we use OpenCV to open any file type")

import cv2

#1st arg is pathname, 2nd is optional flag as to how represent? (-1, 0, 1) (img_unchanged, img_grayscale, img_color)
imgUnchanged =cv2.imread('test.jpg', -1)
imgGrayscale =cv2.imread('test.jpg', 0)
imgColor =cv2.imread('test.jpg', 1)

#1st arg is window name, 2nd is image to display [same window name == no additional windows]
cv2.imshow('grayscale image', imgGrayscale)
cv2.imshow('unchanged image', imgUnchanged)
cv2.imshow('color image', imgColor)

# waits for a key press to close the window (0 specifies infinite loop); arg == time(ms) to be displayed, unless 0
cv2.waitKey(0)

#destroy all created windows
cv2.destroyAllWindows()

#1st arg is path - must include extension! 2nd is image to save. This lets us save a file onto disk!
cv2.imwrite('grayscale.jpg', imgGrayscale)

print("\n\nEnd, thank You!")