"""
Author: Alexander Goudemond

Program name: openAnyVideoTest.py

Goal: 	Open a gif, using OpenCV
		works with mp4 as well!

Notes: To do this, we need to loop over all the frames in the sequence, process each frame at a time

	cv2.VideoCapture() 	#creates video capture obhect
	cv2.VideoWriter() 	#saves to disk
	get()				#argument normally 5 or 7 (???)
	isOpened()			#validates video stream
"""

print("\nHello World! Welcome to this program. Here we are going to try open a GIF")

import cv2

# 1st arg is path, 2nd is apiPreference (???)
vid_capture = cv2.VideoCapture('Cars.mp4')

if (vid_capture.isOpened() == False):
    print("Error opening the video file")

# Read fps and frame count
else:
    # Get frame rate information
    # You can replace 5 with CAP_PROP_FPS as well, they are enumerations
    fps = vid_capture.get(5)
    print('Frames per second : ', fps, 'FPS')

    # Get frame count
    # You can replace 7 with CAP_PROP_FRAME_COUNT as well, they are enumerations
    frame_count = vid_capture.get(7)
    print('Frame count : ', frame_count)

while(vid_capture.isOpened()):
    # vid_capture.read() methods returns a tuple, first element is a bool, second is frame
    readyToRead, frame = vid_capture.read()

    if readyToRead == True:
        cv2.imshow('Frame', frame)
    	# 20ms, try to increase the value, say 50 and observe
        cv2.waitKey(500)
    else:
        break

# Release the video capture object
vid_capture.release()
cv2.destroyAllWindows()

print("\n\nEnd, Thank You!\n")
