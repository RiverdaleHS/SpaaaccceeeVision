import numpy as np
import cv2
import threading
from networktables import NetworkTables
import random
import copy


# Wait for connection to Network Tables
cond = threading.Condition()
notified = [False]

def connectionListener(connected, info):
    print(info, '; Connected=%s' % connected)
    with cond:
        notified[0] = True
        cond.notify()

NetworkTables.initialize(server="localhost")
NetworkTables.addConnectionListener(connectionListener, immediateNotify=True)

with cond:
    print("Waiting")
    if not notified[0]:
        cond.wait()


print("Connected!")
sd = NetworkTables.getTable("SmartDashboard")



#set up default HSV levels
sd.putNumber("H-", 10)
sd.putNumber("H+", 110)#180 max
sd.putNumber("S-", 180)
sd.putNumber("S+", 255)#255 max
sd.putNumber("V-", 100)
sd.putNumber("V+", 255)#255 max

# Set up camera streaming bools
sd.putBoolean("Stream Original", False)
sd.putBoolean("Stream Binary", False)
sd.putBoolean("Stream Contours", False)



while True:
	# Get the latest settings from Smart Dashboard
	hue_min = sd.getNumber("H-", 0)
	hue_max = sd.getNumber("H+", 180)
	saturation_min = sd.getNumber("S-", 0)
	saturation_max = sd.getNumber("S+", 255)
	value_min = sd.getNumber("V-", 0)
	value_max = sd.getNumber("V+", 255)

	# Developmet - needs to be converted to accept video later
	frame_original = cv2.imread("2016_images/0.jpg")
	frame_hsv = cv2.cvtColor(frame_original, cv2.COLOR_BGR2HSV)
	frame_binary = cv2.inRange(frame_hsv, (hue_min, saturation_min, value_min), (hue_max, saturation_max, value_max))
	contours, hierarchy = cv2.findContours(frame_binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	frame_contours = frame_original
	cv2.drawContours(frame_contours, contours, -1, (0, 255, 0), 3)

	cv2.imshow("Original", frame_original)
	cv2.imshow("Binary", frame_binary)
	cv2.imshow("Contours", frame_original)
	if cv2.waitKey(1) & 0xFF == ord('q'):
 		break
	

cv2.destroyAllWindows()



	


