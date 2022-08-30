# from picamera.array import PiRGBArray
# from picamera import PiCamera
# import cv2
# import numpy as np
import gpiozero

# camera = PiCamera()
image_width = 640
image_height = 480
#camera.resolution = (image_width, image_height)
#camera.framerate = 32
# rawCapture = PiRGBArray(camera, size=(image_width, image_height))
center_image_x = image_width / 2
center_image_y = image_height / 2
minimum_area = 250
maximum_area = 100000
# camera.start_preview(fullscreen=False)



robot = gpiozero.Robot(left=(9,10), right=(8,7))
forward_speed = 0.5
turn_speed = 0.3

from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time
# construct the argument parse and parse the arguments

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
    help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
    help="max buffer size")
args = vars(ap.parse_args())


HUE_VAL = 16

lower_color = np.array([HUE_VAL-10,100,100])
upper_color = np.array([HUE_VAL+10, 255, 255])


# if not args.get("video", False):
#     vs = VideoStream(src=0).start()
# # otherwise, grab a reference to the video file
# else:
vs = VideoStream(0).start()
# allow the camera or video file to warm up
time.sleep(2.0)

# for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
#     image = frame.array
#     print(image)
#     hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

while True:
    # grab the current frame
    frame = vs.read()
    # handle the frame from VideoCapture or VideoStream

    #frame = frame[1] if args.get("video", False) else frame

    # if we are viewing a video and we did not grab a frame,
    # then we have reached the end of the video
    if frame is None:
        break
    # resize the frame, blur it, and convert it to the HSV
    # color space
    frame = imutils.resize(frame, width=600)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    color_mask = cv2.inRange(hsv, lower_color, upper_color)

    countours, hierarchy = cv2.findContours(color_mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    object_area = 0
    object_x = 0
    object_y = 0

    for contour in countours:
        x, y, width, height = cv2.boundingRect(contour)
        found_area = width * height
        center_x = x + (width / 2)
        center_y = y + (height / 2)
        if object_area < found_area:
            object_area = found_area
            object_x = center_x
            object_y = center_y
    if object_area > 0:
        ball_location = [object_area, object_x, object_y]
    else:
        ball_location = None

    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    
    
    if ball_location:
        if (ball_location[0] > minimum_area) and (ball_location[0] < maximum_area):
            if ball_location[1] > (center_image_x + (image_width/3)):
                robot.right(turn_speed)
                print("Turning right")
            elif ball_location[1] < (center_image_x - (image_width/3)):
                robot.left(turn_speed)
                print("Turning left")
            else:
                robot.forward(forward_speed)
                print("Forward")
        elif (ball_location[0] < minimum_area):
            robot.left(turn_speed)
            print("Target isn't large enough, searching")
        else:
            robot.stop()
            print("Target large enough, stopping")
    else:
        robot.left(turn_speed)
        print("Target not found, searching")
    
    
    #rawCapture.truncate(0)