# Live video streaming over network with openCV and imagezmq

Implement two Python scripts:

A client that will capture frames from a simple webcam and a server that will take the input frames and run object detection on them.

Reference article: https://www.pyimagesearch.com/2019/04/15/live-video-streaming-over-network-with-opencv-and-imagezmq/

Instruction to setup:
1) Install python 3.7 for windows 10, 64 or 32 but based on your PC.  
2) Configure system environmental variable, path, by adding this line. "C:\Users\your_Username\AppData\Local\Programs\Python\Python37".  Please change user name accordingly. 
3) Open cmd as an admin. Run "python" you should be able to python version. If yes, exit using ctrl+D or type exit(). If you are seeing an error saying "python isn't available" or similar error.  Check for any online resource, on how to configure environmental varible for python.  
4) Create a virtual environment for Python by running "python -m venv virutal_environment_name"
5) cd virutal_environment_name in cmd. And, type "Scripts\activate" to activate the virutal environment.  
6) Copy the downloaded folder from this repository into this directory. Run the command "pip install -r requirements.txt"
7) Installation takes some time. Do this in both sender and receiver PC.
8) In Sender PC: Run "python client.py -s <IP Address>" 
9) In Receiver PC: Run "python server.py"
