import zmq

def recv_array_from_camera_server(socket, flags=0, copy=True, track=False):
    """
        A function to receive array from camera server

        Args:
            socket (object): socket sobject
            flags (int): flag for socket
            copy (boolean): Set to True
            track(boolean): Set to False

        Returns:
            image: Returns frame
    """
    md = socket.recv_json(flags=flags)
    msg = socket.recv(flags=flags, copy=copy, track=track)
    buf = memoryview(msg)
    A = np.frombuffer(buf, dtype=md['dtype'])
    return A.reshape(md['shape'])

  def send_array(socket, A, output_json, flags=0, copy=True, track=False):
    """
        A function to send a numpy array with metadata

        Args:
            socket (object): socket object
            A (image): Image array
            output_json (json): Json response
            flags(int): Flag is set to 0 by default
            copy(boolean): Set to True
            track(boolean): Set to False

        Returns:
            object: Returns the socket object
    """
    md = dict(
        dtype=str(A.dtype),
        shape=A.shape,
        opJson=output_json,
    )
    socket.send_json(md, flags | zmq.SNDMORE)
    return socket.send(A, flags, copy=copy, track=track)
  
print("[INFO] Waiting for the client user to send IP address of the cam server...")
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")
ip_add_camera_server = socket.recv()
print(f"[INFO] Received the IP address of cam server: {str(ip_add_cam_server)} ")
ip = str(ip_add_cam_server)
print("[INFO] Connecting to cam server...")
context = zmq.Context()
socket_c = context.socket(zmq.REP)
tcp = "tcp://" + ip[2:-1] + ":5555"
socket_c.connect(tcp)
i = 0
while i < 1:
    i = i + 1
    # Receiving the frame
    frame = recv_array_from_camera_server(socket_c)
    print("[INFO] Received the frame")
    
output_json = {} # Dummy json
send_array(socket, frame, output_json)
            
while True:
    print("[INFO] Waiting for the client to send messages...")
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")
    msg = socket.recv()
    print(f"[INFO] Received the message: {msg} ")
    socket.send_string("Message received")
    socket.close()
