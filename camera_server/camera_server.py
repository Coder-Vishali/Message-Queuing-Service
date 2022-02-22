import zmq
import numpy as np
import cv2

# ----------------------------------------------------------------
# Aurco marker detection
# ----------------------------------------------------------------

def aruco_detection(frame):
    """
        A function to detect aurco markers

        Args:
            frame(image): This is the frame received from camera server

        Returns:
            image: Returns the cropped image after detection of aruco markers
    """
    first_aruco = ()
    bottom_aruco = ()

    # change the get parameter. according to the finder script
    aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_1000)
    aruco_params = cv2.aruco.DetectorParameters_create()
    (corners, ids, rejected) = cv2.aruco.detectMarkers(frame, aruco_dict, parameters=aruco_params)
    if len(corners) > 0:

        ids = ids.flatten()

        for (markerCorner, markerID) in zip(corners, ids):
            corners_reshape = markerCorner.reshape((4, 2))
            if markerID == 200:
                (top_left, top_right, bottom_right, bottom_left) = corners_reshape
                bottom_aruco = (int(top_left[0]), int(top_left[1]))

            if markerID == 50:
                (top_left_1, top_right_1, bottom_right_1, bottom_left_1) = corners_reshape
                first_aruco = (int(bottom_right_1[0]), int(bottom_right_1[1]))

        crop_img = frame[int(first_aruco[1]):int(bottom_aruco[1]), int(first_aruco[0]):int(bottom_aruco[0])]
        cv2.imwrite(f"crop_frame.jpg", crop_img)

# ----------------------------------------------------------------
# Receive the frame
# ----------------------------------------------------------------

def recv_array(socket, flags=0, copy=True, track=False):
    """
        A function to receive camera frames

        Args:
            socket (object): socket object
            flags(int): Flag is set to 0 by default
            copy(boolean): Set to True
            track(boolean): Set to False

        Returns:
            image: Returns the frame
    """
    md = socket.recv_json(flags=flags)
    msg = socket.recv(flags=flags, copy=copy, track=track)
    buf = memoryview(msg)
    A = np.frombuffer(buf, dtype=md['dtype'])
    return A.reshape(md['shape'])


# ----------------------------------------------------------------
# Send the json & image response
# ----------------------------------------------------------------


def send_array(socket, A, flags=0, copy=True, track=False):
    """send a numpy array with metadata"""
    md = dict(
        dtype=str(A.dtype),
        shape=A.shape,
    )
    socket.send_json(md, flags | zmq.SNDMORE)
    return socket.send(A, flags, copy=copy, track=track)


while True:
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.bind("tcp://*:5555")
    vid = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    vid.set(cv2.CAP_PROP_AUTOFOCUS, 0)  # turn the autofocus on
    vid.set(cv2.CAP_PROP_FRAME_WIDTH, 3200)  # 7680, 2560
    vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 1800)  # 4320, 1440
    vid.set(cv2.CAP_PROP_BRIGHTNESS, 110)
    vid.set(cv2.CAP_PROP_CONTRAST, 80)
    vid.set(cv2.CAP_PROP_SATURATION, 80)
    vid.set(cv2.CAP_PROP_EXPOSURE, -2)
    i = 0
    # Which frame you want to send
    # it seems like first frame goes poor as compared the the later ones.
    FRAME = 2
    while i <= FRAME:
        ret, frame = vid.read()
        if i == FRAME:
            print("%s Frame captured" % i)
        else:
            print("%s Frame captured but skipped" % i)
        i = i + 1
    print("Frame captured %s ..." % ret)
    # Aruco marker detection
    aruco_detection(frame)
    crop_image = cv2.imread("crop_frame.jpg")
    print("[INFO] Performed aruco marker detections\n")
    print("[INFO] Waiting for the client user to connect...")
    send_array(socket, crop_image)
    print("[INFO] Sent the frame to the client user\n")
vid.release()
