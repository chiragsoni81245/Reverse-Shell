import socket

s = socket.socket()

s.connect( ("127.0.0.1",9999) )

while True:
	data = s.recv(1024)
	if len(data)>0:
		print( "Server:>>{}".format( str(data,"utf-8") ) )
	msg = input("Message:>>")
	s.send( str.encode( msg ) )

