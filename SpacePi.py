from cscore import CameraServer
import cv2
import numpy as np
import threading
from networktables import NetworkTables
import subprocess
import math

cond = threading.Condition()
notified = [False]

def connectionListener(connected, info):
	print(info, '; Connected=%s' % connected)
	with cond:
		notified[0] = True
		cond.notify()

NetworkTables.initialize(server='Henrys-MacBook-Pro-47.local')
NetworkTables.addConnectionListener(connectionListener, immediateNotify=True)

with cond:
	print("Waiting")
	if not notified[0]:
		cond.wait()

print("Connected!")

table = NetworkTables.getTable('SpaceVision')
table.putNumber("hue_min", 55)
table.putNumber("hue_max", 75)#180
table.putNumber("sat_min", 0)
table.putNumber("sat_max", 255)#255
table.putNumber("val_min", 30)
table.putNumber("val_max", 100)#255

# table.putNumber("min Target Area", 50)
# table.putNumber("min aspect_ratio", 0)
# table.putNumber("max Target Area", 50)
# table.putNumber("max aspect_ratio", 0)

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
	all_targets = []
	frame_contour = np.zeros(shape=(240, 320, 3), dtype=np.uint8)


	for contour in contours:
		x,y,w,h = cv2.boundingRect(contour)
		cX = int(x + w/2)
		cY = int(y + h/2)
		cv2.circle(frame_contour, (cX, cY), 2, (255,255,255), -1)


		if len(contour) <= 5:
			break
		try:
			(x,y),(MA,ma),angle = cv2.fitEllipse(contour)
			if 10 < angle < 20:
				positive_targets.append(contour)
				all_targets.append(contour)
			if 175 > angle > 155: #this could be tighened up but there may be issues
				negative_targets.append(contour)
				all_targets.append(contour)
		except:
			pass


	best_target = None
	best_target_filled = False
	for target in all_targets:
		if best_target_filled == False:
			best_target_filled = True
			best_target = target
		else:
			bx, by, bw, bh = cv2.boundingRect(best_target)
			b_error = 160 - bx
			tx, ty, tw, th = cv2.boundingRect(target)
			t_error = 160 - tx
			if abs(t_error) < abs(b_error):
				best_target = target

	match_target = None
	match_target_filled = False
	if best_target_filled:
		(x,y),(MA,ma),angle = cv2.fitEllipse(best_target)
		bx, by, bw, bh = cv2.boundingRect(best_target)

		center_target_has_positive_polarity = False
		if 10 < angle < 20:
			center_target_has_positive_polarity = True
		possible_matching_targets = []
		if center_target_has_positive_polarity:
			possible_matching_targets = negative_targets
		else:
			possible_matching_targets = positive_targets

		for possible_matching_target in possible_matching_targets:
			if match_target_filled == False:
				match_target_filled = True
				match_target = possible_matching_target
			else:
				mx, my, mw, mh = cv2.boundingRect(best_target)
				m_error = bx - mx
				pmx, pmy, pmw, pmh = cv2.boundingRect(possible_matching_target)
				t_error = bx - pmx
				if abs(t_error) < abs(m_error):
					match_target = possible_matching_target

	if match_target_filled:
		ax, ay, aw, ah = cv2.boundingRect(best_target)
		bx, by, bw, bh = cv2.boundingRect(match_target)
		cx = ((ax + aw/2) + (bx + bw/2))/2
		cy = ((ay + ah/2) + (by + bh/2))/2
		cv2.circle(frame_contour, (int(cx), int(cy)), 5, (0, 0, 255), -1)
		yawAngle = math.atan((cx - 159.5)/6.664471244677486084e+02)
		pitchAngle = math.atan((cy - 119.5)/6.736390397611033904e+02)

		table.putNumber("Target X", cx)
		table.putNumber("Target Y", cy)
		table.putNumber("Yaw Angle", math.degrees(yawAngle))
		table.putNumber("Pitch Angle", math.degrees(pitchAngle))

		#experiment with larger resolution



	cv2.drawContours(frame_contour, [best_target], -1, (255, 0, 0), 4)
	cv2.drawContours(frame_contour, [match_target], -1, (0, 0, 255), 4)
	
	imageStream.putFrame(img)
	binaryStream.putFrame(frame_binary)
	contourStream.putFrame(frame_contour)



























