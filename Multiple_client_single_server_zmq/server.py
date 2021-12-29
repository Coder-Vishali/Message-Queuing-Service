import zmq

while True:
    print("[INFO] Waiting for the client to send messages...")
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")
    msg = socket.recv()
    print(f"[INFO] Received the message: {msg} ")
    socket.send_string("Message received")
    socket.close()
