from cscore import CameraServer
import cv2
import numpy as np
import threading
from networktables import NetworkTables
import subprocess

cond = threading.Condition()
notified = [False]

def connectionListener(connected, info):
	print(info, '; Connected=%s' % connected)
	with cond:
		notified[0] = True
		cond.notify()

NetworkTables.initialize(server='192.168.0.5')
NetworkTables.addConnectionListener(connectionListener, immediateNotify=True)

with cond:
	print("Waiting")
	if not notified[0]:
		cond.wait()

print("Connected!")

table = NetworkTables.getTable('SpaceVision')
table.putNumber("hue_min", 0)
table.putNumber("hue_max", 180)#180
table.putNumber("sat_min", 0)
table.putNumber("sat_max", 255)#255
table.putNumber("val_min", 0)
table.putNumber("val_max", 255)#255

cs = CameraServer.getInstance()
cs.enableLogging()

camera = cs.startAutomaticCapture()
camera.setResolution(320, 240)
subprocess.call(["./setup_camera.sh"])

# Get a CvSink. This will capture images from the camera
cvSink = cs.getVideo()

# (optional) Setup a CvSource. This will send images back to the Dashboard
outputStream = cs.putVideo("Name", 320, 240)

img = np.zeros(shape=(240, 320, 3), dtype=np.uint8)

while True:
	time, img = cvSink.grabFrame(img)
	if time == 0:
		outputStream.notifyError(cvSink.getError());
		continue

	hue_min = table.getNumber("hue_min", 0)
	hue_max = table.getNumber("hue_max", 180)
	sat_min = table.getNumber("sat_min", 0)
	sat_max = table.getNumber("sat_max", 255)
	val_min = table.getNumber("val_min", 0)
	val_max = table.getNumber("val_max", 255)
	#img processing
	frame_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	frame_binary = cv2.inRange(frame_hsv, (hue_min, sat_min, val_min), (hue_max, sat_max, val_max))



	outputStream.putFrame(frame_binary)




























