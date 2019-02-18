import sys
import socket
import threading

MAX_CHUNK_SIZE = 1024
PROXY_ADDR = '127.0.0.1'
PORT = 8080 #default port

"""
Thread class that deals with a connection from a client and processes it then sends it to the specified webserver
"""
class connThread(threading.Thread):
    # thread setup
    def __init__(self, threadID, addr, port):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.addr = addr
        self.port = port
        self.setDaemon(True)
    # thread execution
    def run(self):
        print('starting thread', self.threadID)
        clientToProxy(self.threadID, self.addr, self.port)
        print('exiting thread', self.threadID)

"""
Class is for parsing HTTP requests into their components
"""
class request():
    # set initial values
    def __init__(self, request_str):
        self.request_str = request_str
        self.webserver = ""
        self.port = -1
    # parse request
    def parse(self):
        first = self.request_str.split('\n')[0]
        url = first.split(' ')[1]
    
        http_pos = url.find("://")
        if (http_pos == -1):
            temp = url
        else:
            temp = url[(http_pos + 3):]
    
        port_pos = temp.find(":")

        webserver_pos = temp.find("/")
        if (webserver_pos == -1):
            webserver_pos = len(temp)

        if (port_pos == -1 or webserver_pos < port_pos):
            self.port = PORT
            self.webserver = temp[:webserver_pos]
        else:
            port = int((temp[(port_pos + 1):])[:webserver_pos - port_pos - 1])
            self.webserver = temp[:port_pos]

def clientToProxy(threadID, addr, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((addr, port))
    while True:
        sock.listen()
        conn, conn_addr = sock.accept()
        with conn:
            print('connected by', conn_addr)
            data = conn.recv(MAX_CHUNK_SIZE)
            if not data:
                break
            else:
                request_str = data.decode()
                print(request_str)
                req = request(request_str)
                req.parse()
                print(req.webserver)
                print(req.port)

def proxyToServer(threadID, addr, port, request):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.connect((addr, port))
    sock.sendall(request)

thread = connThread(1, PROXY_ADDR, PORT)
thread.start()
thread.join()
