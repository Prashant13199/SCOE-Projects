from gpiozero import DistanceSensor
from time import sleep
import os

sensor = DistanceSensor(24, 23)
os.system("espeak 'Distance Calculating' -s 120")

while True:
	distance = sensor.distance * 100
	print('Distance to nearest object is', distance, 'cm')
	
	sleep(1)
