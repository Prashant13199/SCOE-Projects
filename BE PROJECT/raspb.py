import socket
from gpiozero import Robot
import time
from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import numpy as np
from collections import deque
from imutils.video import VideoStream
import imutils

UDP_IP = "0.0.0.0" # listen to everything
UDP_PORT = 12345 # port
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

image_width = 640
image_height = 480
center_image_x = image_width / 2
center_image_y = image_height / 2
minimum_area = 250
maximum_area = 100000

robot = Robot(left=(9,10), right=(8,7))
forward_speed = 0.4
turn_speed = 0.2

HUE_VAL = 16

lower_color = np.array([HUE_VAL-10,100,100])
upper_color = np.array([HUE_VAL+10, 255, 255])
vs = VideoStream('http://192.168.1.101:8000/stream.mjpg').start()
time.sleep(2.0)

while True:
    data, addr = sock.recvfrom(7) # random buffer size, doesn't matter here..
    print("received message:", data)
    if data==b'left':
        print("left")
        robot.left(0.2)

    elif data==b'right':
        print("right")
        robot.right(0.2)


    elif data==b'forward':
        print("forward")
        robot.forward(0.3)

    elif data==b"search":
        print('searching')
        robot.right(0.2)

    elif data==b'clear':
        robot.stop()
        print('clear')
        data=' '
        print(data)
        print('@@')
    elif data == b'reset':
        print('reset')
        while True:
            frame = vs.read()
            if frame is None:
                break
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
                    time.sleep(0.1)
                    robot.left(0.5)
                    time.sleep(1)
                    robot.stop()
                    time.sleep(1)
                    print("Target large enough, stopping")
                    break
            else:
                robot.left(turn_speed)
                print("Target not found, searching")
                
                  

