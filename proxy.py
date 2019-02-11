import sys, io
import socket
import threading
from http.server import BaseHTTPRequestHandler

MAX_CHUNK_SIZE = 1024
PROXY_ADDR = '127.0.0.1'
PORT = 8080

class c2p_thread(threading.Thread):
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
        client_to_proxy(self.threadID, self.addr, self.port)
        print('exiting thread', self.threadID)

class HTTPRequest(BaseHTTPRequestHandler):
    # HTTP request parsing
    def __init__(self, request):
        self.rfile = io.StringIO(request)
        self.raw_requestline = self.rfile.readline()
        self.error_code = self.error_message = None
        self.parse_request()
    # HTTP error handling
    def send_error(self, code, message):
        self.error_code = code
        self.error_message = message

def client_to_proxy(threadID, addr, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((addr, port))
    while True:
        sock.listen()
        conn, conn_addr = sock.accept()
        with conn:
            print('connected by', conn_addr)
            request = conn.recv(MAX_CHUNK_SIZE)
            if not request:
                break
            else:
                request = request.decode()
                request = HTTPRequest(request)
                print(request.error_code)
                print(request.command)
                print(request.path)
                print(request.request_version)
                print(len(request.headers))
                print(request.headers.keys())
                print(request.headers['host'])

thread = c2p_thread(1, PROXY_ADDR, PORT)
thread.start()
thread.join()
