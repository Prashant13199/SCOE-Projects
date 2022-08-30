from flask import Flask
from flask import render_template, Response, redirect, url_for, session, request
import time
from gpiozero import Robot
import picamera
import cv2
import socket 
import io

vc = cv2.VideoCapture(0)





app = Flask(__name__,template_folder='template')

robot = Robot(left=(9, 10), right=(8, 7))

@app.route("/")
def index():
    return render_template('robot.html')

@app.route('/left_side')
def left_side():
    data1="LEFT"
    robot.left()
    return 'true'

@app.route('/right_side')
def right_side():
   data1="RIGHT"
   robot.right()
   return 'true'

@app.route('/up_side')
def up_side():
   data1="FORWARD"
   robot.forward()
   return 'true'

@app.route('/down_side')
def down_side():
   data1="BACK"
   robot.backward()
   return 'true'

@app.route('/stop')
def stop():
   data1="STOP"
   robot.stop()
   return  'true'

def gen(): 
   """Video streaming generator function.""" 
   while True: 
       rval, frame = vc.read() 
       cv2.imwrite('pic.jpg', frame) 
       yield (b'--frame\r\n' 
              b'Content-Type: image/jpeg\r\n\r\n' + open('pic.jpg', 'rb').read() + b'\r\n') 
@app.route('/video_feed') 
def video_feed(): 
   """Video streaming route. Put this in the src attribute of an img tag.""" 
   return Response(gen(), 
                   mimetype='multipart/x-mixed-replace; boundary=frame')




if __name__ == "__main__":
 print('start')
 app.run(host='192.168.2.19',port=3000)


