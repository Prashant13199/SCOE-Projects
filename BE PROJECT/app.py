
from pyimagesearch.centroidtracker import CentroidTracker
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import time
import cv2
import socket
import telegram
import threading
import os
import cv2
import face_recognition
import cv2
import numpy as np
import os
import glob

#UDP connection for Raspberry-Pi
UDP_IP = "192.168.1.101"
UDP_PORT = 12345
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

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
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])


#initializing video input
#cam = cv2.VideoCapture(0)
# vs = VideoStream(src=0).start()
vs = VideoStream(src='http://192.168.1.101:8000/stream.mjpg').start()
cam = cv2.VideoCapture('http://192.168.1.101:8000/stream.mjpg')
cam.set(3, 640)
cam.set(4, 480)
time.sleep(2.0)
fps = FPS().start()

#face initialization
faces_encodings = []
faces_names = []
cur_direc = os.getcwd()
path = os.path.join(cur_direc, 'data/faces/')
list_of_files = [f for f in glob.glob(path+'*.jpg')]
number_files = len(list_of_files)
names = list_of_files.copy()

#face training
for i in range(number_files):
    globals()['image_{}'.format(i)] = face_recognition.load_image_file(list_of_files[i])
    globals()['image_encoding_{}'.format(i)] = face_recognition.face_encodings(globals()['image_{}'.format(i)])[0]
    faces_encodings.append(globals()['image_encoding_{}'.format(i)])
# Create array of known names
    names[i] = names[i].replace(cur_direc, "")  
    faces_names.append(names[i])


#Telegram Bot setup
bot = telegram.Bot(token="1469663121:AAH_06ZWTOM3AdLb7vA3_pmN3hFMdzTML_k")
#bot = telegram.Bot(token="1670471660:AAH9x5vj87VaEismlV06u7K9n0EvCKOut8Y")
chat_id = 1409170051
store = 0
temp10 = 0
out = cv2.VideoWriter('video.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 30.0, (640, 480))
print("Starting Process, Check Telegram for updates")
bot.sendMessage(text = '/start\n1. Send STOP to stop following', chat_id=chat_id)

#checking new messages or commands from user
def check_msg():
    updates = bot.getUpdates(timeout=1000)
    for i in updates:
        last = i.message.text
        msgid = i.message.message_id
    return last,msgid

# multiprocessing for sending unknown person image
def multi(temp10):
	bot.sendPhoto(chat_id=chat_id, photo=open('image{}.jpg'.format(temp10), 'rb'))

def multi2(temp10):
	unknown_image = face_recognition.load_image_file("image{}.jpg".format(temp10))
	try:
		unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
		matches = face_recognition.compare_faces (faces_encodings, unknown_encoding)
		if(matches[0] == True):
			os.remove('image{}.jpg'.format(temp10))
			sock.sendto(b'stop', (UDP_IP, UDP_PORT))
			store = msgid
			print('Known person found')
			bot.sendMessage(text = 'Known Person found', chat_id=chat_id)
			sock.sendto(b'reset', (UDP_IP, UDP_PORT))
			time.sleep(100)
		os.remove('image{}.jpg'.format(temp10))
	except:
		print('Not able to detect face')

while True:
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

	if objects:
		ret , img = cam.read()
		out.write(img)
		if temp10<2:
			cv2.imwrite('image{}.jpg'.format(temp10), frame)
			threading.Thread(target=multi(temp10)).start()
			threading.Thread(target=multi2(temp10)).start()
			temp10+=1
		if centroid[0] > 280:
			print("Turning Right")
			sock.sendto(b'clear', (UDP_IP, UDP_PORT))
			sock.sendto(b'right', (UDP_IP, UDP_PORT))
		elif centroid[0] < 120:
			print("Turning left")
			sock.sendto(b'clear', (UDP_IP, UDP_PORT))	
			sock.sendto(b'left', (UDP_IP, UDP_PORT))
		else:
			print("Forward")
			sock.sendto(b'clear', (UDP_IP, UDP_PORT))	
			sock.sendto(b'forward', (UDP_IP, UDP_PORT))
	else:
		print("Search")
		sock.sendto(b'clear', (UDP_IP, UDP_PORT))
		sock.sendto(b'search', (UDP_IP, UDP_PORT))
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF
	if key == ord("q"):
		break
	fps.update()

	msg,msgid = check_msg()
	if(msg == 'STOP' and msgid>store):
		sock.sendto(b'stop', (UDP_IP, UDP_PORT))
		store = msgid
		out.release()
		print('Stopped Following')
		bot.sendMessage(text = 'Stopped Following', chat_id=chat_id)
		temp10 = 0
		try:
			bot.sendVideo(chat_id=chat_id, video=open('video.mp4', 'rb'),timeout=1000)
			#os.remove('video.mp4')
			print('Video Sent')
		except:
			print('Unable to send video')
		cam.release
		time.sleep(10)

	if(msg == 'RESET' and msgid>store):
		store = msgid
		bot.sendMessage(text = 'Known Person', chat_id=chat_id)
		sock.sendto(b'stop', (UDP_IP, UDP_PORT))
		sock.sendto(b'reset', (UDP_IP, UDP_PORT))
		time.sleep(100)
	
	if(msg == 'SEND PHOTO' and msgid>store):
		store = msgid
		cv2.imwrite('image.jpg',frame)
		bot.sendPhoto(chat_id=chat_id, photo=open('image.jpg', 'rb'))
		os.remove('image.jpg')
		
fps.stop()
print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
cv2.destroyAllWindows()
vs.stop()
