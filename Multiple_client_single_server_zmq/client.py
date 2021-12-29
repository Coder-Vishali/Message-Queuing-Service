import zmq
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-s", "--server-ip", required=True,
                help="ip address of the server to which the client will connect")
args = vars(ap.parse_args())

context = zmq.Context()
print("Connecting to server...")
socket = context.socket(zmq.REQ)
socket.connect("tcp://{}:5555".format(args["server_ip"]))
socket.send_string("Hello world")
print("Sent the message")
print(socket.recv())
socket.close()
