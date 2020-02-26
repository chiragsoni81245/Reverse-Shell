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
	def listener(self):
            self.s.bind((self.host,self.port))
            self.s.listen(5)

            add,con = self.s.accept()
            print("Connection Established with {} :>".format(add))
            while True:
                key = con.recv(100);

                print( key.decode() )



if __name__=="__main__":
	shell = ReverseShell("",9999)
	shell.listener()
