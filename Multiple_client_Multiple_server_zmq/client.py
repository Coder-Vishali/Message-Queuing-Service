import zmq
import argparse
import cv2
import numpy as np
import json
from datetime import datetime

def recv_array(socket, flags=0, copy=True, track=False):
    md = socket.recv_json(flags=flags)
    msg = socket.recv(flags=flags, copy=copy, track=track)
    buf = memoryview(msg)
    A = np.frombuffer(buf, dtype=md['dtype'])
    return A.reshape(md['shape']), md['opJson']

def send_array(socket, A, flags=0, copy=True, track=False):
    md = dict(
        dtype=str(A.dtype),
        shape=A.shape,
    )
    socket.send_json(md, flags | zmq.SNDMORE)
    return socket.send(A, flags, copy=copy, track=track)

begin_time = datetime.now()
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--camera_server-ip", required=True,
                help="ip address of the camera server to which the client user will connect")
ap.add_argument("-s", "--pipeline_server-ip", required=True,
                help="ip address of the pipeline server to which the client user will connect")

args = vars(ap.parse_args())
print("[INFO] Connecting to centralised pipeline server...")
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://{}:5555".format(args["pipeline_server_ip"]))

socket.send_string(args["camera_server_ip"])
print("[INFO] Sent the camera server IP address to the centralised pipeline server")
print("[INFO] Waiting for the response from centralised pipeline server...")
frame, opJson = recv_array(socket)
with open('output.json', 'w', encoding='utf-8') as opJ:
    json.dump(opJson, opJ, ensure_ascii=False, indent=4)
now = datetime.now()
dt_string = now.strftime("%d_%m_%Y_%H_%M_%S")
cv2.imwrite(f"frame_od_{dt_string}.jpg", frame)
print("[INFO] Received frame and json response from pipeline server")
socket.close()
print("[INFO] Execution time: ", datetime.now() - begin_time)

# To execute this script:
# python client.py -c <ip_addres_of_camera_server> -s <ip_address_of_centralised_server> 
