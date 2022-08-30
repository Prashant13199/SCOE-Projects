from gpiozero import DistanceSensor, Robot
from time import sleep
import os
#from picamera import PiCamera

sensor = DistanceSensor(24, 23)
os.system("espeak 'Starting Cleaning Mode' -s 120")
robot = Robot(left=(9, 10), right=(8, 7))
speed = 0.4

print("Starting Process")
while True:
    #camera = PiCamera()
    #camera.start_preview(fullscreen=False)
    distance = sensor.distance*100
    if distance>20:
        print(distance)
        robot.forward(speed)
        sleep(0.1)
    else:
        robot.left(0.3)
        sleep(0.1)
    sleep(0.1)
