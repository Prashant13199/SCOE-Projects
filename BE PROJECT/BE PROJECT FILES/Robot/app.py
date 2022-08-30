import cv2
import os
import telegram
import time
import datetime
from pyimagesearch.centroidtracker import CentroidTracker
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('trainer/trainer.yml')
cascadePath = "haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascadePath)

#cam = cv2.VideoCapture('http://192.168.2.100:8000/stream.mjpg')
cam = cv2.VideoCapture(0)

cam.set(3, 640)
cam.set(4, 480)

minW = 0.1*cam.get(3)
minH = 0.1*cam.get(4)



ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prototxt", required=True,
	help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model", required=True,
	help="path to Caffe pre-trained model")
ap.add_argument("-c", "--confidence", type=float, default=0.2,
	help="minimum probability to filter weak detections")
args = vars(ap.parse_args())

ct = CentroidTracker()

CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
	"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
	"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
	"sofa", "train", "tvmonitor"]
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

# load our serialized model from disk
print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])


store = 0
font = cv2.FONT_HERSHEY_SIMPLEX
id = 0
names = ['None', 'Prashant']

bot = telegram.Bot(token="1311459740:AAEAanAx6yY48hQUi7HFijOW5MMhGxU6N8I")
chat_id = 1296216215

print("Starting Process")

bot.sendMessage(text = '/start', chat_id=chat_id)

bot.sendMessage(text = 'Booting Up..', chat_id=chat_id)

bot.sendMessage(text = 'Starting Surveillance', chat_id=chat_id)

def check_msg():
    updates = bot.getUpdates(timeout=1000)
    for i in updates:
        last = i.message.text
        msgid = i.message.message_id
    return last,msgid

while True:

	temp = 0
	ret, img = cam.read()

	gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
	
	faces = faceCascade.detectMultiScale(gray,scaleFactor = 1.2,minNeighbors = 5,minSize = (int(minW), int(minH)),)
	
	for(x,y,w,h) in faces:

		cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)

		id, confidence = recognizer.predict(gray[y:y+h,x:x+w])

		if (confidence < 100):
			id22 = names[id]
			print(id22)
		
		else:
			id22 = "Unknown Person Detected"
			print(id22)
			cv2.imwrite('image.png', img)
			bot.sendMessage(text = 'Unknown Person Detected', chat_id=chat_id,timeout=1000)
			bot.sendPhoto(chat_id=chat_id, photo=open('image.png', 'rb'))
			os.remove('image.png')
			bot.sendMessage(text = 'Following', chat_id=chat_id)
			print("starting video stream...")
			vs = VideoStream(src=0).start()
			time.sleep(2.0)
			fps = FPS().start()
			while True:
				msg,msgid = check_msg()
				frame = vs.read()
				frame = imutils.resize(frame, width=400)
				(h, w) = frame.shape[:2]
				blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
					0.007843, (300, 300), 127.5)
				net.setInput(blob)
				detections = net.forward()
				rects = []
				# loop over the detections
				for i in np.arange(0, detections.shape[2]):
					confidence = detections[0, 0, i, 2]

					if confidence > args["confidence"]:
						idx = int(detections[0, 0, i, 1])
						#print(idx)
						if idx == 15:
							box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
							(startX, startY, endX, endY) = box.astype("int")
							rects.append(box.astype("int"))
							label = "{}: {:.2f}%".format(CLASSES[idx],
								confidence * 100)
							cv2.rectangle(frame, (startX, startY), (endX, endY),
								(0, 255, 0), 2)
							y = startY - 15 if startY - 15 > 15 else startY + 15
							cv2.putText(frame, label, (startX, y),
								cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)
					
				objects = ct.update(rects)
				# loop over the tracked objects
				for (objectID, centroid) in objects.items():
					text = "ID {}".format(objectID)
					cv2.circle(frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)

				cv2.imshow("frame",frame)

				if(msg == 'Stop' and msgid>store):
					store = msgid
					temp = 1
					print('Stopped Following')
					bot.sendMessage(text = 'Stopped Following', chat_id=chat_id)
					vs.stop()
					fps.stop()
					break
			fps.update()
		if temp == 1:
			break
				
			print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
			print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
			
		
	msg,msgid = check_msg()
	if(msg == 'Send video' and msgid>store):
		store = msgid
		print('Sending video please wait...')
		bot.sendMessage(text = 'Sending video please wait..', chat_id=chat_id)
		out = cv2.VideoWriter('video.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 20.0, (640, 480))
		capture_duration=10
		start_time = time.time()
		while int(time.time() - start_time) < capture_duration:
			ret ,cap = cam.read()
			out.write(cap)
		
		out.release()
		bot.sendVideo(chat_id=chat_id, video=open('video.mp4', 'rb'),timeout=1000)
		os.remove('video.mp4')
		print('Video Sent')