import sys
import socket
import _thread

MAX_CHUNK_SIZE = 99999999
PROXY_ADDR = '127.0.0.1'
PORT = 8080 #default port
BLACKLIST = []

"""
Request class for parsing HTTP requests into their components
"""
class request():
    # set initial values
    def __init__(self, request_str):
        self.request_str = request_str
        self.req_type = ""
        self.webserver = ""
        self.port = -1
    # parse request
    def parse(self):
        self.req_type = self.request_str.split(' ')[0]
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
            self.port = 5000
            self.webserver = temp[:webserver_pos]
        else:
            port = int((temp[(port_pos + 1):])[:webserver_pos - port_pos - 1])
            self.webserver = temp[:port_pos]

def proxy(conn, conn_addr):
    while True:
        data = conn.recv(MAX_CHUNK_SIZE)

        if not data:
            break
        else:
            request_str = data.decode("latin-1")
            print("Request: {}".format(request_str))

            req = request(request_str)
            req.parse()

            for i in range(len(BLACKLIST)):
                if (req.webserver == BLACKLIST[i]):
                    print("The hostname {} is blocked".format(req.webserver))
                    conn.close()
                    break
    conn.close()

def main():

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        sock.close()
        print("Could not open socket")
        sys.exit(1)

    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((PROXY_ADDR, PORT))
    sock.listen()

    while True:
        conn, conn_addr = sock.accept()
        thread = _thread.start_new_thread(proxy, (conn, conn_addr))
        print("Connected by ", conn_addr)

        cmd = input("Type 'block' to block URLs\n")
        if (cmd == "block"):
            cmd = input("Enter the URL(s) you would like to block separated by spaces\n")
            BLACKLIST.append(cmd.split())
            print("Blocked URLs: ", BLACKLIST)
        else:
            print("Invalid command")

if __name__ == "__main__":
    main()
