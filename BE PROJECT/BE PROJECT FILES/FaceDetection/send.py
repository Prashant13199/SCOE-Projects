
import subprocess
from subprocess import Popen, PIPE, STDOUT
import json
import requests
import re
import cv2
import numpy as np
import os
import telegram
import time
import datetime

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('trainer/trainer.yml')
cascadePath = "haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascadePath)

cam = cv2.VideoCapture(0)

cam.set(3, 640)
cam.set(4, 480)

minW = 0.1*cam.get(3)
minH = 0.1*cam.get(4)

store = 0
temp = 0
font = cv2.FONT_HERSHEY_SIMPLEX
id = 0
names = ['None', 'Prashant']

cmd = "ssh -R 80:localhost:8080 ssh.localhost.run"

bot = telegram.Bot(token="1289776508:AAGHpjWzhhsk_KBtBaMs4UpQ0pQtY7R3s0o")
chat_id = 1296216215

p = subprocess.Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT)

while True:
	line = p.stdout.readline()
	content = line.decode("utf8")
	web = re.findall("http://pi-\w+[.]localhost[.]run",content)
	if(web and temp == 0):
	    url = 'Streaming Link: '+ web[0]
	    bot.sendMessage(text = url, chat_id=chat_id)
	    bot.sendMessage(text = 'Setting link: https://admin.localhost.run/', chat_id=chat_id)
	    temp = 1
	    break

def check_msg():
    updates = bot.getUpdates(chat_id=chat_id)
    for i in updates:
        last = i.message.text
        msgid = i.message.message_id
    return last,msgid

while True:
	ret, img = cam.read()
	
	gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

	faces = faceCascade.detectMultiScale(gray,scaleFactor = 1.2,minNeighbors = 5,minSize = (int(minW), int(minH)),)
	
	for(x,y,w,h) in faces:

		cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)

		id, confidence = recognizer.predict(gray[y:y+h,x:x+w])
		# Check if confidence is less them 100 ==> "0" is perfect match
		if (confidence < 100):
			id22 = names[id]
			cv2.imwrite('image.png', img)
			bot.sendMessage(text = names[id], chat_id=chat_id)
			bot.sendPhoto(chat_id=chat_id, photo=open('image.png', 'rb'))
			os.remove('image.png')
		
		else:
			id22 = "unknown"
			cv2.imwrite('imagee.png', img)
			bot.sendMessage(text = 'Unknow Person Detected', chat_id=chat_id)
			bot.sendPhoto(chat_id=chat_id, photo=open('imagee.png', 'rb'))
			os.remove('imagee.png')
		
	msg,msgid = check_msg()
	
	if(msg == 'Send video' and msgid>store):
		cam.release()
		store = msgid
		print('Sending video please wait...')
		os.system('raspivid -t 10000 -w 640 -h 480 -fps 25 -b 1200000 -p 0,0,640,480 -o pivideo.h264')
		os.system('MP4Box -add pivideo.h264 pivideo.mp4')
		os.system('rm pivideo.h264')
		bot.sendMessage(text = 'sending video', chat_id=chat_id)
		bot.sendVideo(chat_id=chat_id, video=open('pivideo.mp4', 'rb'))
		os.remove('pivideo.mp4')
		cam = cv2.VideoCapture(0)
		cam.set(3, 640)
		cam.set(4, 480)
		minW = 0.1*cam.get(3)
		minH = 0.1*cam.get(4)
