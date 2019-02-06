import socket
import threading
import sys

MAX_CHUNK_SIZE = 1024
PROXY_ADDR = '127.0.0.1'
PORT = 8080

num_threads = int(sys.argv[1])

class c2p_thread(threading.Thread):
    # method for thread setup
    def __init__(self, threadID, addr, port):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.addr = addr
        self.port = port
    # method for thread execution
    def run(self):
        print('starting thread', self.threadID)
        client_to_proxy(self.threadID, self.addr, self.port)
        print('exiting thread', self.threadID)

def client_to_proxy(threadID, addr, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((addr, port))
    while True:
        s.listen()
        conn, conn_addr = s.accept()
        with conn:
            print('connected by', conn_addr)
            data = conn.recv(MAX_CHUNK_SIZE)
            if not data:
                break
            else:
                data_str = data.decode()
                print('received:', data)

try:
    for t in range(num_threads):
        thread = c2p_thread(t, PROXY_ADDR, (PORT+t))
        thread.start()
        thread.join()
        break
except:
    print('error: unable to start thread(s)')
