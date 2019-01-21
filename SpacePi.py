from cscore import CameraServer
import cv2
import numpy as np
import threading
from networktables import NetworkTables

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

# Insert your processing code here
print("Connected!")

table = NetworkTables.getTable('SpaceVision')

cs = CameraServer.getInstance()
cs.enableLogging()

# Capture from the first USB Camera on the system
camera = cs.startAutomaticCapture()
camera.setResolution(320, 240)

# Get a CvSink. This will capture images from the camera
cvSink = cs.getVideo()

# (optional) Setup a CvSource. This will send images back to the Dashboard
outputStream = cs.putVideo("Name", 320, 240)

# Allocating new images is very expensive, always try to preallocate
img = np.zeros(shape=(240, 320, 3), dtype=np.uint8)

while True:
    # Tell the CvSink to grab a frame from the camera and put it
    # in the source image.  If there is an error notify the output.
    time, img = cvSink.grabFrame(img)
    if time == 0:
        # Send the output the error.
        outputStream.notifyError(cvSink.getError());
        # skip the rest of the current iteration
        continue

    #
    # Insert your image processing logic here!
    #

    # (optional) send some image back to the dashboard
    outputStream.putFrame(img)