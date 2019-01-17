import cv2
import math

hue_min = 0 # 10
hue_max = 180 #180
sat_min = 0 #0
sat_max = 75 #255
val_min = 240 #0
val_max = 255 #255


cap = cv2.VideoCapture(1)
def nothing(x):
	pass

cv2.namedWindow("trackbar")
cv2.createTrackbar('hue_min','trackbar',0,180,nothing)
cv2.createTrackbar('hue_max','trackbar',0,180,nothing)
cv2.createTrackbar('sat_min','trackbar',0,255,nothing)
cv2.createTrackbar('sat_max','trackbar',0,255,nothing)
cv2.createTrackbar('val_min','trackbar',0,255,nothing)
cv2.createTrackbar('val_max','trackbar',0,255,nothing)


while True:
	# hue_min = cv2.getTrackbarPos('hue_min','trackbar')
	# hue_max = cv2.getTrackbarPos('hue_max','trackbar')
	# sat_min = cv2.getTrackbarPos('sat_min','trackbar')
	# sat_max = cv2.getTrackbarPos('sat_max','trackbar')
	# val_min = cv2.getTrackbarPos('val_min','trackbar')
	# val_max = cv2.getTrackbarPos('val_max','trackbar')


	ret, frame_original = cap.read()
#frame_original = cv2.imread("CargoAngledDark48in.jpg")
	frame_hsv = cv2.cvtColor(frame_original, cv2.COLOR_BGR2HSV)
	frame_binary = cv2.inRange(frame_hsv, (hue_min, sat_min, val_min), (hue_max, sat_max, val_max))
	contours, hierarchy = cv2.findContours(frame_binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

	positive_targets = []
	negative_targets = []
	vision_things = []

	for contour in contours:
		#solidity
		area = cv2.contourArea(contour)
		hull = cv2.convexHull(contour)
		hull_area = cv2.contourArea(hull)
		# if area == 0:
		# 	break
		x,y,w,h = cv2.boundingRect(contour)
		aspect_ratio = float(w)/h
		# if aspect_ratio > 0.5:
		# 	pass
		if area < 50:
			pass
		

		vision_things.append(contour)
		#solidity = float(area)/hull_area
		#angle
		# if len(contour) <= 5:
		# 	break
		try:
			(x,y),(MA,ma),angle = cv2.fitEllipse(contour)
			if angle < 30:
				positive_targets.append(contour)
			if angle > 150:
				negative_targets.append(contour)
		except:
			pass




	targets = []

	for i, pt in enumerate(positive_targets):

		try:
			nt = negative_targets[i]
			targets.append([pt, nt])
		except:
			pass


	for t in targets:
		try:
			p_M = cv2.moments(t[0])
			p_cX = int(p_M["m10"] / p_M["m00"])
			p_cY = int(p_M["m01"] / p_M["m00"])

			n_M = cv2.moments(t[1])
			n_cX = int(n_M["m10"] / n_M["m00"])
			n_cY = int(n_M["m01"] / n_M["m00"])

			meanX = (p_cX + n_cX)/2
			meanY = (p_cY + n_cY)/2

			cv2.circle(frame_original,(int(meanX),int(meanY)), 5, (255,0,), -1)

			yawAngle = math.atan((meanX - 159.5)/6.664471244677486084e+02)
		except:
			pass
		# print(yawAngle)
		# print(math.degrees(yawAngle))


	#print(vision_things)
	cv2.drawContours(frame_original, contours, -1, (0, 0, 0), 3)
	cv2.drawContours(frame_original, positive_targets, -1, (0, 255, 0), 5)
	cv2.drawContours(frame_original, negative_targets, -1, (0, 0, 255), 5)
	cv2.drawContours(frame_original, vision_things, -1, (0, 50, 50), 3)


	cv2.imshow("Binary", frame_binary)
	cv2.imshow("Original", frame_original)

	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
cap.release()
#cv2.waitKey(0)
cv2.destroyAllWindows()
