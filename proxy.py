import sys
import socket
import threading
from random import randint

MAX_CHUNK_SIZE = 1024
PROXY_ADDR = '127.0.0.1'
PORT = 8080 #default port
BLACKLIST = []

"""
Thread class that deals with a connection from a client and processes it then sends it to the specified webserver
"""
class connThread(threading.Thread):
    # thread setup
    def __init__(self, threadID, socket):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.socket = socket
    # thread execution
    def run(self):
        print('Starting thread', self.threadID)
        clientToProxy(self.threadID, self.socket)
        print('Exiting thread', self.threadID)

"""
Request class for parsing HTTP requests into their components
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

"""
Function for dealing with incoming connections
"""
def clientToProxy(threadID, conn):
    while True:
        data = conn.recv(MAX_CHUNK_SIZE)

        if not data:
            break
        else:
            request_str = data.decode()
            print("Thread {}: {}".format(threadID, request_str))

            req = request(request_str)
            req.parse()
            print("Thread {}: webserver {}".format(threadID, req.webserver))
            print("Thread {}: port {}".format(threadID, req.port))

            for i in range(len(BLACKLIST)):
                if (req.webserver == BLACKLIST[i]):
                    print("Thread {}: The hostname {} is blocked".format(threadID, req.webserver))
                    conn.close()
                    break

            proxyToServer(threadID, req.webserver, req.port, data, conn)

    conn.close()

"""
Function for dealing with outgoing connections
"""
def proxyToServer(threadID, addr, port, request, conn):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.connect((addr, port))
        sock.sendall(request)
    except socket.error:
        if sock:
            sock.close()
        print("Could not open socket")
        sys.exit(1)

    while True:
        data = sock.recv(MAX_CHUNK_SIZE)
        if not data:
            break
        else:
            str = data.decode()
            print("Thread {}: {}".format(threadID, str))
            conn.send(data)

    sock.close()

def main():

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((PROXY_ADDR, PORT))
        sock.listen()
        conn, conn_addr = sock.accept()
        print("Connected by ", conn_addr)

    except socket.error:
        if sock:
            sock.close()
        print("Could not open socket")
        sys.exit(1)

    thread = connThread(randint(1000, 9999), conn)
    thread.start()
    thread.join()

    while True:
        cmd = input("Type 'block' to block URLs\n")
        if (cmd == "block"):
            cmd = input("Enter the URL(s) you would like to block separated by spaces\n")
            BLACKLIST.append(cmd.split())
            print("Blocked URLs: ", BLACKLIST)
        else:
            print("Invalid command")

if __name__ == "__main__":
    main()
