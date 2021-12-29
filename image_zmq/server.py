# import the necessary packages

# To build a montage of all incoming frames.
from imutils import build_montages
from datetime import datetime
import numpy as np
# For streaming video from clients
import imagezmq
import argparse
import imutils
import cv2

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
# The path to our mage verification deep learning prototxt file.
ap.add_argument("-p", "--prototxt", required=True,
	help="path to image verification 'deploy' prototxt file")
# The path to our pre-trained image verification deep learning model.
ap.add_argument("-m", "--model", required=True,
	help="path to image verification pre-trained model")
# Our confidence threshold to filter weak detections.
ap.add_argument("-c", "--confidence", type=float, default=0.2,
	help="minimum probability to filter weak detections")
#  number of columns for our montage
ap.add_argument("-mW", "--montageW", required=True, type=int,
	help="montage frame width")
# The number of rows for your montage
ap.add_argument("-mH", "--montageH", required=True, type=int,
	help="montage frame height")
args = vars(ap.parse_args())

# Our server needs an ImageHub to accept connections from each of the client PC
# Uses sockets and ZMQ for receiving frames across the network
# initialize the ImageHub object
imageHub = imagezmq.ImageHub()
# initialize the list of class labels image verification was trained to
# detect, then generate a set of bounding box colors for each class
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
	"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
	"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
	"sofa", "train", "tvmonitor"]
# load our serialized model from disk
print("[INFO] loading model...")
# instantiate our image verification object detector
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

# initialize the consider set (class labels we care about and want
# to count), the object count dictionary, and the frame  dictionary
# use this CONSIDER set to filter out other classes
CONSIDER = set(["dog", "person", "car"])

#  Initializes a dictionary for our object counts to be tracked
#  in each video feed. Each count is initialized to zero.
objCount = {obj: 0 for obj in CONSIDER}

# The frameDict dictionary will contain the hostname key
# and the associated latest frame value.
frameDict = {}

# initialize the dictionary which will contain  information regarding
# when a device was last active, then store the last time the check
# was made was now

# lastActive dictionary will have hostname keys and timestamps for values.
lastActive = {}
lastActiveCheck = datetime.now()

# stores the estimated number of windows PC, active checking period, and
# calculates the duration seconds to wait before making a check to
# see if a device was active
# Constants which help us to calculate whether a windows is active
# Calculates that our check for activity will be 40 seconds
ESTIMATED_NUM_PIS = 4
ACTIVE_CHECK_PERIOD = 10
ACTIVE_CHECK_SECONDS = ESTIMATED_NUM_PIS * ACTIVE_CHECK_PERIOD

# assign montage width and height so we can view all incoming frames
# in a single "dashboard"
# These values are pulled directly from the command line args dictionary.
mW = args["montageW"]
mH = args["montageH"]
print("[INFO] detecting: {}...".format(", ".join(obj for obj in
	CONSIDER)))

# start looping over all the frames
while True:
	# receive RPi name and frame from the RPi and acknowledge
	# the receipt
	# Grab an image from the imageHub and send an ACK message
	# rpiName - hostname
	(rpiName, frame) = imageHub.recv_image()
	print(frame)
	imageHub.send_reply(b'OK')

	# Perform housekeeping duties to determine when a Windows PC was lastActive .
	# if a device is not in the last active dictionary then it means
	# that its a newly connected device
	if rpiName not in lastActive.keys():
		print("[INFO] receiving data from {}...".format(rpiName))
	# record the last active time for the device from which we just
	# received a frame
	lastActive[rpiName] = datetime.now()

	# resize the frame to have a maximum width of 400 pixels, then
	# grab the frame dimensions and construct a blob
	frame = imutils.resize(frame, width=400)
	(h, w) = frame.shape[:2]

	# A blob is created from the image
	blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
		0.007843, (300, 300), 127.5)

	# The blob is passed through the neural net.
	# pass the blob through the network and obtain the detections and
	# predictions
	net.setInput(blob)
	detections = net.forward()

	# reset the object count for each object in the CONSIDER set
	# reset the object counts to zero
	objCount = {obj: 0 for obj in CONSIDER}

	# loop over the detections
	# looping over each of the detections
	for i in np.arange(0, detections.shape[2]):
		# extract the confidence (i.e., probability) associated with
		# the prediction
		confidence = detections[0, 0, i, 2]
		# filter out weak detections by ensuring the confidence is
		# greater than the minimum confidence
		if confidence > args["confidence"]:
			# extract the index of the class label from the
			# detections
			idx = int(detections[0, 0, i, 1])
			# check to see if the predicted class is in the set of
			# classes that need to be considered
			if CLASSES[idx] in CONSIDER:
				# increment the count of the particular object
				# detected in the frame
				objCount[CLASSES[idx]] += 1
				# compute the (x, y)-coordinates of the bounding box
				# for the object
				box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
				(startX, startY, endX, endY) = box.astype("int")
				# draw the bounding box around the detected object on
				# the frame
				cv2.rectangle(frame, (startX, startY), (endX, endY),
							  (255, 0, 0), 2)

				# let’s annotate each frame with the hostname and object counts.
			    # We’ll also build a montage to display them in

				# draw the sending device name on the frame
				cv2.putText(frame, rpiName, (10, 25),
							cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
				# draw the object count on the frame
				label = ", ".join("{}: {}".format(obj, count) for (obj, count) in
								  objCount.items())
				cv2.putText(frame, label, (10, h - 20),
							cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

				# update the new frame in the frame dictionary
				# update our frameDict with the frame corresponding to the RPi hostname.
				frameDict[rpiName] = frame

                # Create and display a montage of our client frames.
				# The montage will be mW frames wide and mH frames tall.
				# build a montage using images in the frame dictionary
				montages = build_montages(frameDict.values(), (w, h), (mW, mH))
				# display the montage(s) on the screen
				for (i, montage) in enumerate(montages):
					cv2.imshow("Home pet location monitor ({})".format(i),
							   montage)

				# detect any kepresses
				key = cv2.waitKey(1) & 0xFF

				# The last block is responsible for checking our lastActive timestamps
			    # for each client feed and removing frames from the montage that have stalled.

				# if current time *minus* last time when the active device check
				# was made is greater than the threshold set then do a check
				if (datetime.now() - lastActiveCheck).seconds > ACTIVE_CHECK_SECONDS:
					# loop over all previously active devices
					# loop over each key-value pair in lastActive
					for (rpiName, ts) in list(lastActive.items()):
						# remove the RPi from the last active and frame
						# dictionaries if the device hasn't been active recently
						if (datetime.now() - ts).seconds > ACTIVE_CHECK_SECONDS:
							print("[INFO] lost connection to {}".format(rpiName))
							# If the device hasn’t been active recently we need to remove data.
							# First we remove the rpiName and timestamp from lastActive.
							# Then the rpiName and frame are removed from the frameDict
							lastActive.pop(rpiName)
							frameDict.pop(rpiName)
					# set the last active check time as current time
					lastActiveCheck = datetime.now()
				# Effectively this will help us get rid of expired frames
				# (i.e. frames that are no longer real-time).
				#  The worst thing that could happen if you don’t get rid of   #  expired frames is that an intruder kills power to a client
				# and you don’t realize the frame isn’t updating.
				# if the `q` key was pressed, break from the loop
				if key == ord("q"):
					break
			# do a bit of cleanup
			cv2.destroyAllWindows()

'''		
python server.py --prototxt MobileNetSSD_deploy.prototxt --model MobileNetSSD_deploy.caffemodel --montageW 2 --montageH 2
'''