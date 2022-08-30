import socket
from gpiozero import Robot
import time
from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import numpy as np
import gpiozero

UDP_IP = "0.0.0.0" # listen to everything
UDP_PORT = 12345 # port
robot = Robot(left=(9, 10), right=(8, 7))
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

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
        robot.forward(0.4)

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
        
          

