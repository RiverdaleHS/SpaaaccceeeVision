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
table.putNumber("hue_min", 55)
table.putNumber("hue_max", 72)#180
table.putNumber("sat_min", 80)
table.putNumber("sat_max", 150)#255
table.putNumber("val_min", 85)
table.putNumber("val_max", 220)#255

table.putNumber("min Target Area", 50)
table.putNumber("min aspect_ratio", 0)
table.putNumber("max Target Area", 50)
table.putNumber("max aspect_ratio", 0)

cs = CameraServer.getInstance()
cs.enableLogging()

camera = cs.startAutomaticCapture()
camera.setResolution(320, 240)
subprocess.call(["./setup_camera.sh"])

# Get a CvSink. This will capture images from the camera
cvSink = cs.getVideo()

# (optional) Setup a CvSource. This will send images back to the Dashboard
imageStream = cs.putVideo("Image Stream", 320, 240)
binaryStream = cs.putVideo("Binary Stream", 320, 240)
contourStream = cs.putVideo("Contour Stream", 320, 240)

img = np.zeros(shape=(240, 320, 3), dtype=np.uint8)

while True:
	time, img = cvSink.grabFrame(img)
	if time == 0:
		imageStream.notifyError(cvSink.getError());
		binaryStream.notifyError(cvSink.getError());
		contourStream.notifyError(cvSink.getError());
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
	_, contours, _ = cv2.findContours(frame_binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

	positive_targets = []
	negative_targets = []

	for contour in contours:
		#solidity
		area = cv2.contourArea(contour)
		hull = cv2.convexHull(contour)
		hull_area = cv2.contourArea(hull)
		x,y,w,h = cv2.boundingRect(contour)
		aspect_ratio = float(w)/h

		if area < table.getNumber("min Target Area", 50):
			break

		if aspect_ratio < table.getNumber("min aspect_ratio", 0):
			break
		
		if area > table.getNumber("max Target Area", 50):
			break

		if aspect_ratio > table.getNumber("max aspect_ratio", 0):
			break
		#solidity = float(area)/hull_area
		#angle
		# if len(contour) <= 5:
		# 	break
		# try:
		# 	(x,y),(MA,ma),angle = cv2.fitEllipse(contour)
		# 	if angle < 30:
		# 		positive_targets.append(contour)
		# 	if angle > 150:
		# 		negative_targets.append(contour)


		# except:
		# 	pass
		positive_targets.append(contour)

	frame_contour = np.zeros(shape=(240, 320, 3), dtype=np.uint8)
	cv2.drawContours(frame_contour, contours, -1, (255, 0, 0), 1)
	cv2.drawContours(frame_contour, positive_targets, -1, (0, 255, 0), 1)
	cv2.drawContours(frame_contour, negative_targets, -1, (0, 0, 255), 1)
	
	imageStream.putFrame(img)
	binaryStream.putFrame(frame_binary)
	contourStream.putFrame(frame_contour)



























