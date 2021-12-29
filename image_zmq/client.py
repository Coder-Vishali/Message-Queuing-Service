# import the necessary packages
# VideoStream will be used to grab frames from our camera.
from imutils.video import VideoStream
# Used for real-time streaming
import imagezmq
# Used to process a command line argument containing the server’s IP address
import argparse
# Used to grab the hostname of the windows client
import socket
# Used to allow our camera to warm up prior to sending frames.
import time
import imutils
import cv2

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-s", "--server-ip", required=True,
	help="ip address of the server to which the client will connect")
args = vars(ap.parse_args())

# initialize the ImageSender object with the socket address of the server
# Specified the IP address and port of the server
sender = imagezmq.ImageSender(connect_to="tcp://{}:5555".format(
	args["server_ip"]))

# get the host name, initialize the video stream, and allow the
# camera sensor to warmup
hostName = socket.gethostname()

# use any USB camera connected to the PC
# vs = VideoStream(src=0).start()
# set your camera resolution to maximum resolution
# If you find that there is a lag, you are likely sending too many pixels.
# If that is the case, you may reduce your resolution quite easily.
vs = VideoStream(src=0).start()
time.sleep(2.0)

# Grabs and sends the frames.
while True:
    # read the frame from the camera and send it to the server
    frame = vs.read()
    # As an alternative, you can resize the frame manually
    #frame = imutils.resize(frame, width=320)
    sender.send_image(hostName, frame)