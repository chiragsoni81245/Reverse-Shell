import socket




def socket_bind():
	try:
		s.bind( ("",9999) )
		s.listen(2)
		conn,address = s.accept()
		send_message(conn)
		conn.close()
	except:
		print("Error in binding\n Retrying...")
		socket_bind()

def send_message(conn):

	while True:
		text = input("Message:>>")
		conn.send( str.encode(text) )
		response = str( conn.recv(1024), "utf-8" )
		print( "Client:>>{}".format(response) )


s = socket.socket()
socket_bind()

