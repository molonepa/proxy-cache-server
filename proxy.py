import sys
import socket
import threading

MAX_CHUNK_SIZE = 2048
PROXY_ADDR = '127.0.0.1' #host address
PORT = 8080 #default port
BLACKLIST = [['example.org']] #blocked URLs

"""
Request class for parsing HTTP/HTTPS requests into their components
"""
class HTTPRequest():
    # set initial values
    def __init__(self, data):
        self.data = data
        self.req_type = ""
        self.webserver = ""
        self.port = -1
    # parse request
    def parse(self):
        # HTTP/HTTPS
        self.req_type = self.data.split(b' ')[0]

        first = self.data.split(b'\n')[0]
        url = first.split(b' ')[1]
    
        http_pos = url.find(b"://")
        if (http_pos == -1):
            temp = url
        else:
            temp = url[(http_pos + 3):]
    
        port_pos = temp.find(b":")

        webserver_pos = temp.find(b"/")
        if (webserver_pos == -1):
            webserver_pos = len(temp)

        if (port_pos == -1 or webserver_pos < port_pos):
            self.port = 5000
            self.webserver = temp[:webserver_pos]
        else:
            port = int((temp[(port_pos + 1):])[:webserver_pos - port_pos - 1])
            self.webserver = temp[:port_pos]
"""
Proxy handler function to be executed by thread
"""
def proxyThread(client_sock):
    data = client_sock.recv(MAX_CHUNK_SIZE)

    print("Request: {}".format(data.decode()))

    req = HTTPRequest(data)
    req.parse()

    for i in range(len(BLACKLIST)):
        print('*\n')
        if (req.webserver == BLACKLIST[i]):
            print("The hostname {} is blocked".format(req.webserver))
            client_sock.close()
            break

    try:
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.connect((req.webserver, req.port))
        print("Connection established with {}:{}".format(req.webserver, req.port))
    except socket.error:
        server_socket.close()
        print("Could not open socket")
        sys.exit(1)

    if (req.req_type == b"CONNECT"):
        try:
            response = b"HTTP/1.0 200 Connection established\r\nProxy-agent: Pyx\r\n\r\n"
            client_sock.sendall(response)
        except socket.error:
            print("Connection could not be established")
    else:
        server_sock.sendall(data)

    while True:
        try:
            request = client_sock.recv(MAX_CHUNK_SIZE)
            server_sock.sendall(request)
        except socket.error:
            print("Error sending request to server")
        try:
            response = server_sock.recv(MAX_CHUNK_SIZE)
            client_sock.sendall(response)
        except socket.error:
            print("Error sending response to client")
        except KeyboardInterrupt:
            print("Exiting...")
            server_sock.close()
            client_sock.close()
            sys.exit(0)
"""
Main function initialises listening socket and starts threads for each incoming connection
"""
def main():
    try:
        proxy_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        proxy_sock.close()
        print("Could not open socket")
        sys.exit(1)

    proxy_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    proxy_sock.bind((PROXY_ADDR, PORT))
    proxy_sock.listen()

    while True:
        client_sock, client_addr = proxy_sock.accept()
        print("Connected by ", client_addr)

        threading.Thread(target=proxyThread, args=(client_sock,)).start()

        cmd = input(" ")
        if (cmd == "block"):
            cmd = input("Enter the URL(s) you would like to block separated by spaces\n")
            BLACKLIST.append(cmd.split())
            print("Blocked URLs: ", BLACKLIST)
        else:
            print("Invalid command")

if __name__ == "__main__":
    main()
